#!/usr/bin/env python3
"""Read-only public GitHub portfolio status; no third-party packages required."""

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

OWNER = "vlovers"
REPOSITORIES = (
    "grid-atlas",
    "ai-office",
    "rulewitness",
    "mutation-boundary",
    "estima",
    "last-chapter",
)
BASE = "https://api.github.com"
# Existing baseline PRs only. This is a read-only review queue, not a merge queue.
FOUNDATION_PRS = (
    ("grid-atlas", 268),
    ("ai-office", 43),
    ("rulewitness", 82),
    ("mutation-boundary", 68),
    ("estima", 13),
    ("vlovers", 2),
    ("last-chapter", 5),
)

# Separate review lanes: intake and CI/supply-chain changes remain unmerged until
# their own review and required checks. Tracking a PR is not an authorization.
SHA_PATTERN = re.compile(r"[0-9a-fA-F]{40}$")


def validate_sha(value):
    if not isinstance(value, str) or not SHA_PATTERN.fullmatch(value):
        raise ValueError("Invalid Git commit SHA")
    return value


def safe_markdown_cell(value):
    """Fail closed on malformed metadata and escape Markdown table delimiters."""
    if not isinstance(value, str) or not value or len(value) > 255:
        raise ValueError("Invalid GitHub text metadata")
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise ValueError("Control character in GitHub metadata")
    return value.replace(chr(92), chr(92) * 2).replace("|", chr(92) + "|")


FOLLOWUP_PRS = (
    ("grid-atlas", 271, "issue intake"),
    ("grid-atlas", 272, "CI security"),
    ("ai-office", 48, "issue intake"),
    ("ai-office", 49, "CI security"),
    ("rulewitness", 83, "issue intake"),
    ("mutation-boundary", 69, "issue intake"),
    ("mutation-boundary", 70, "CI security"),
    ("estima", 14, "issue intake"),
    ("estima", 15, "CI security"),
)


def request(path):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "vlovers-portfolio-status",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(BASE + path, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.load(response)



def summarize_workflow_runs(response, expected_sha):
    """Conservative observation of PR workflow runs, not required-check certification."""
    if not isinstance(response, dict):
        raise ValueError("Malformed Actions response")
    runs = response.get("workflow_runs")
    total = response.get("total_count")
    if not isinstance(runs, list) or type(total) is not int or total < len(runs):
        raise ValueError("Malformed Actions pagination metadata")
    if total > len(runs):
        return "unknown (incomplete Actions pagination)"
    if any(not isinstance(run, dict) for run in runs):
        raise ValueError("Malformed Actions run")
    if not runs or any(run.get("head_sha") != expected_sha for run in runs):
        return "unknown (no exact-SHA evidence)"
    valid_statuses = {"queued", "in_progress", "completed", "requested", "waiting", "pending"}
    valid_conclusions = {
        None, "success", "failure", "timed_out", "cancelled", "action_required",
        "startup_failure", "neutral", "skipped", "stale",
    }
    for run in runs:
        status, conclusion = run.get("status"), run.get("conclusion")
        if not isinstance(status, str) or status not in valid_statuses:
            raise ValueError("Invalid Actions run status")
        if conclusion is not None and not isinstance(conclusion, str):
            raise ValueError("Invalid Actions run conclusion")
        if conclusion not in valid_conclusions:
            raise ValueError("Unknown Actions run conclusion")
    failed = {"failure", "timed_out", "cancelled", "action_required", "startup_failure"}
    if any(run.get("conclusion") in failed for run in runs):
        return "failure observed"
    if any(run.get("status") != "completed" for run in runs):
        return "pending"
    if all(run.get("conclusion") == "success" for run in runs):
        return f"{len(runs)}/{len(runs)} observed success"
    return "unknown (non-success conclusion)"



def summarize_review_evidence(reviews, expected_sha, author_login):
    """Review observations only: never branch protection or independent acceptance."""
    validate_sha(expected_sha)
    if not isinstance(reviews, list) or not isinstance(author_login, str) or not author_login:
        raise ValueError("Incomplete PR review metadata")
    latest_decisive = {}
    for review in reviews:
        if not isinstance(review, dict) or not isinstance(review.get("user"), dict):
            raise ValueError("Malformed review identity")
        user = review["user"]
        login = user.get("login")
        kind = user.get("type")
        if not isinstance(login, str) or not login or kind not in {"User", "Bot", "Organization", "Mannequin"}:
            raise ValueError("Incomplete review identity or account type")
        state = review.get("state")
        if state not in ("APPROVED", "CHANGES_REQUESTED", "DISMISSED", "COMMENTED", "PENDING"):
            raise ValueError("Invalid GitHub review state")
        if login.lower() == author_login.lower() or kind != "User":
            continue
        if state in {"APPROVED", "CHANGES_REQUESTED", "DISMISSED"}:
            # GitHub's PR reviews endpoint lists reviews chronologically.
            latest_decisive[login.lower()] = review
    if any(review["state"] == "CHANGES_REQUESTED" for review in latest_decisive.values()):
        return "changes requested observed (not cleared)"
    approvals = sum(
        review["state"] == "APPROVED" and review.get("commit_id") == expected_sha
        for review in latest_decisive.values()
    )
    if approvals:
        return f"{approvals} head-SHA non-author approval(s) observed (not acceptance)"
    if any(review["state"] == "APPROVED" for review in latest_decisive.values()):
        return "historical approvals only (not head-SHA)"
    return "no head-SHA non-author approval observed"


def fetch_pr_reviews(repo, number):
    """Retrieve every review page; incomplete responses cannot certify approval."""
    reviews = []
    for page in range(1, 21):
        batch = request(f"/repos/{repo}/pulls/{number}/reviews?per_page=100&page={page}")
        if not isinstance(batch, list):
            raise ValueError("Malformed PR review response")
        reviews.extend(batch)
        if len(batch) < 100:
            return reviews
    raise ValueError("PR review pagination exceeded safety limit")

def fetch_pr_metadata(name, number, cache=None):
    """Reuse PR metadata within one report run; never persist it across runs."""
    key = (name, number)
    if cache is not None and key in cache:
        return cache[key]
    repo = urllib.parse.quote(OWNER + "/" + name, safe="/")
    pr = request(f"/repos/{repo}/pulls/{number}")
    if not isinstance(pr, dict):
        raise ValueError("Malformed PR metadata")
    if cache is not None:
        cache[key] = pr
    return pr


def summarize_mergeability(pr):
    """GitHub mergeability is transient; it is never merge authorization."""
    value = pr.get("mergeable")
    if value is True:
        return "mergeable observed (not clearance)"
    if value is False:
        return "not mergeable observed (investigate)"
    if value is None:
        return "unknown (GitHub pending)"
    raise ValueError("Malformed PR mergeability metadata")


def foundation_pr_status(name, number, pr_cache=None):
    repo = urllib.parse.quote(OWNER + "/" + name, safe="/")
    pr = fetch_pr_metadata(name, number, pr_cache)
    sha = validate_sha(pr["head"]["sha"])
    state = "merged" if pr.get("merged_at") else pr["state"]
    if state not in {"open", "closed", "merged"}:
        raise ValueError("Unexpected PR state")
    runs = request(
        f"/repos/{repo}/actions/runs?event=pull_request&head_sha={sha}&per_page=100"
    )
    author_login = (pr.get("user") or {}).get("login")
    review = summarize_review_evidence(fetch_pr_reviews(repo, number), sha, author_login)
    return state, sha, summarize_workflow_runs(runs, sha), review, summarize_mergeability(pr)


def render_pr_queue(title, entries, show_lane=False, pr_cache=None):
    """Render a tracked queue; return count of failed lookups (unknown != green)."""
    errors = 0
    print(f"\n## {title}")
    lane_column = " | Lane" if show_lane else ""
    print(f"| Repository / PR{lane_column} | State | Head SHA | Observed PR workflow runs | Review observation | GitHub mergeability |")
    print("| ---" + (" | ---" if show_lane else "") + " | --- | --- | --- | --- | --- |")
    for item in entries:
        name, number = item[:2]
        lane = f" | {item[2]}" if show_lane else ""
        label = f"[{name} #{number}](https://github.com/{OWNER}/{name}/pull/{number})"
        try:
            state, sha, ci, review, mergeability = foundation_pr_status(name, number, pr_cache)
            print(f"| {label}{lane} | {state} | `{sha[:12]}` | {ci} | {review} | {mergeability} |")
        except (KeyError, TypeError, urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError) as exc:
            print(f"| {label}{lane} | unknown | unknown | unknown | unknown | unknown |")
            print(f"Warning: could not read tracked PR {name} #{number}: {exc}", file=sys.stderr)
            errors += 1
    return errors


# Monitor every tracked, unmerged engineering PR against its live target.
# Do not use PR base.sha as today's target tip: it can be a historical ancestor.
BRANCH_DRIFT_PRS = tuple(
    (name, number)
    for name, number, *_ in (*FOUNDATION_PRS, *FOLLOWUP_PRS)
    if (name, number) != ("grid-atlas", 268)
)


def summarize_branch_divergence(compare):
    """Count commits unique to live base vs PR; this is NOT conflict detection."""
    if not isinstance(compare, dict):
        raise ValueError("Malformed compare response")
    if compare.get("status") not in {"identical", "ahead", "behind", "diverged"}:
        raise ValueError("Unexpected compare status")
    base_only = compare.get("ahead_by")
    pr_only = compare.get("behind_by")
    if any(type(value) is not int or value < 0 for value in (base_only, pr_only)):
        raise ValueError("Invalid compare commit counts")
    return f"base-only {base_only}; PR-only {pr_only} ({compare['status']})"


def branch_drift_status(name, number, pr_cache=None):
    """Compare PR HEAD against the *live named base ref*, not PR base.sha."""
    repo = urllib.parse.quote(OWNER + "/" + name, safe="/")
    pr = fetch_pr_metadata(name, number, pr_cache)
    head = validate_sha(pr["head"]["sha"])
    base = pr["base"]["ref"]
    if not isinstance(base, str) or not base or "/" in base or any(
        char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-" for char in base
    ):
        raise ValueError("Invalid PR base ref for compare")
    # HEAD...BASE: ahead_by counts commits unique to the base; behind_by
    # counts commits unique to the PR. The base ref resolves at query time.
    compare = request(
        f"/repos/{repo}/compare/{head}...{urllib.parse.quote(base, safe='')}"
    )
    return head, base, summarize_branch_divergence(compare)


def render_branch_drift_queue(pr_cache=None):
    """Report integration risk without interpreting divergence as a merge conflict."""
    errors = 0
    print("\n## Engineering PR branch freshness — live base ref (not merge clearance)")
    print("| PR | Head SHA | Base branch | Commit divergence |")
    print("| --- | --- | --- | --- |")
    for name, number in BRANCH_DRIFT_PRS:
        label = f"[{name} #{number}](https://github.com/{OWNER}/{name}/pull/{number})"
        try:
            sha, base, status = branch_drift_status(name, number, pr_cache)
            print(f"| {label} | `{sha[:12]}` | `{base}` | {status} |")
        except (KeyError, TypeError, urllib.error.HTTPError, urllib.error.URLError,
                TimeoutError, ValueError) as exc:
            print(f"| {label} | unknown | unknown | unknown |")
            print(f"Warning: could not compare {name} #{number}: {exc}", file=sys.stderr)
            errors += 1
    return errors


def count_open_items(owner_repo, endpoint, exclude_pull_requests=False):
    """Count all pages conservatively; never silently truncate a large queue."""
    count = 0
    seen_numbers = set()
    for page in range(1, 21):
        items = request(f"/repos/{owner_repo}/{endpoint}?state=open&per_page=100&page={page}")
        if not isinstance(items, list) or len(items) > 100 or any(
            not isinstance(item, dict) or type(item.get("number")) is not int
            or item["number"] <= 0
            or ("pull_request" in item and not isinstance(item["pull_request"], dict))
            for item in items
        ):
            raise ValueError(f"Malformed {endpoint} listing")
        for item in items:
            number = item["number"]
            if number in seen_numbers:
                raise ValueError(f"Duplicate {endpoint} item across pages")
            seen_numbers.add(number)
            if not (exclude_pull_requests and "pull_request" in item):
                count += 1
        if len(items) < 100:
            return count
    raise ValueError(f"{endpoint} pagination exceeded safety limit")


def main():
    errors = 0
    pr_cache = {}
    print("# Portfolio GitHub status (live read-only query)\n")
    print("| Repository | Default branch HEAD | Open PRs | Open issues | Latest GitHub release |")
    print("| --- | --- | ---: | ---: | --- |")
    for name in REPOSITORIES:
        owner_repo = urllib.parse.quote(OWNER + "/" + name, safe="/")
        try:
            metadata = request(f"/repos/{owner_repo}")
            branch = metadata["default_branch"]
            if not isinstance(branch, str) or not branch or len(branch) > 255 or any(ord(char) < 32 or ord(char) == 127 for char in branch):
                raise ValueError("Invalid default branch name")
            commit = request(f"/repos/{owner_repo}/commits/{urllib.parse.quote(branch, safe='')}")
            head_sha = validate_sha(commit["sha"])
            head = f"[{head_sha[:10]}](https://github.com/{OWNER}/{name}/commit/{head_sha})"
            # GitHub's issues endpoint also lists PRs; never count those as issues.
            issue_count = count_open_items(owner_repo, "issues", exclude_pull_requests=True)
            pr_count = count_open_items(owner_repo, "pulls")
            try:
                release = safe_markdown_cell(request(f"/repos/{owner_repo}/releases/latest")["tag_name"])
            except urllib.error.HTTPError as exc:
                if exc.code != 404:
                    raise
                release = "none"
            print(f"| [{name}](https://github.com/{OWNER}/{name}) | {head} | {pr_count} | {issue_count} | {release} |")
        except (KeyError, TypeError, urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError) as exc:
            print(f"| {name} | unknown | unknown | unknown | unknown |")
            print(f"Warning: could not read {name}: {exc}", file=sys.stderr)
            errors += 1

    errors += render_pr_queue("Foundation PRs — exact head SHA and observed PR Actions", FOUNDATION_PRS, pr_cache=pr_cache)
    errors += render_pr_queue("Follow-up PRs — issue intake and CI security", FOLLOWUP_PRS, show_lane=True, pr_cache=pr_cache)
    errors += render_branch_drift_queue(pr_cache)
    print(
        "\nObserved Actions and review submissions are **not** required-check, branch-rule, "
        "independent-review, product-acceptance, merge or release certification. "
        "A head-SHA approval observation does not establish reviewer independence. "
        "Unknown never means pass."
    )
    if errors:
        print(f"\n{errors} GitHub queries failed; do not treat unknown as zero or green.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
