#!/usr/bin/env python3
"""Read-only public GitHub portfolio status; no third-party packages required."""

import json
import os
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
)

# Separate review lanes: intake and CI/supply-chain changes remain unmerged until
# their own review and required checks. Tracking a PR is not an authorization.
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
    if not isinstance(runs, list) or not isinstance(total, int) or total < len(runs):
        raise ValueError("Malformed Actions pagination metadata")
    if total > len(runs):
        return "unknown (incomplete Actions pagination)"
    if any(not isinstance(run, dict) for run in runs):
        raise ValueError("Malformed Actions run")
    if not runs or any(run.get("head_sha") != expected_sha for run in runs):
        return "unknown (no exact-SHA evidence)"
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
    if not isinstance(reviews, list) or not author_login:
        raise ValueError("Incomplete PR review metadata")
    latest_decisive = {}
    for review in reviews:
        user = review.get("user") or {}
        login = user.get("login")
        if not login:
            raise ValueError("Review without reviewer identity")
        if login.lower() == author_login.lower() or user.get("type") == "Bot":
            continue
        if review.get("state") in {"APPROVED", "CHANGES_REQUESTED", "DISMISSED"}:
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

def foundation_pr_status(name, number):
    repo = urllib.parse.quote(OWNER + "/" + name, safe="/")
    pr = request(f"/repos/{repo}/pulls/{number}")
    sha = pr["head"]["sha"]
    if len(sha) != 40 or any(char not in "0123456789abcdef" for char in sha.lower()):
        raise ValueError("Invalid PR head SHA")
    state = "merged" if pr.get("merged_at") else pr["state"]
    if state not in {"open", "closed", "merged"}:
        raise ValueError("Unexpected PR state")
    runs = request(
        f"/repos/{repo}/actions/runs?event=pull_request&head_sha={sha}&per_page=100"
    )
    author_login = (pr.get("user") or {}).get("login")
    review = summarize_review_evidence(fetch_pr_reviews(repo, number), sha, author_login)
    return state, sha, summarize_workflow_runs(runs, sha), review


def render_pr_queue(title, entries, show_lane=False):
    """Render a tracked queue; return count of failed lookups (unknown != green)."""
    errors = 0
    print(f"\\n## {title}")
    lane_column = " | Lane" if show_lane else ""
    print(f"| Repository / PR{lane_column} | State | Head SHA | Observed PR workflow runs | Review observation |")
    print("| ---" + (" | ---" if show_lane else "") + " | --- | --- | --- | --- |")
    for item in entries:
        name, number = item[:2]
        lane = f" | {item[2]}" if show_lane else ""
        label = f"[{name} #{number}](https://github.com/{OWNER}/{name}/pull/{number})"
        try:
            state, sha, ci, review = foundation_pr_status(name, number)
            print(f"| {label}{lane} | {state} | `{sha[:12]}` | {ci} | {review} |")
        except (KeyError, TypeError, urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError) as exc:
            print(f"| {label}{lane} | unknown | unknown | unknown | unknown |")
            print(f"Warning: could not read tracked PR {name} #{number}: {exc}", file=sys.stderr)
            errors += 1
    return errors


def main():
    errors = 0
    print("# Portfolio GitHub status (live read-only query)\n")
    print("| Repository | Default branch HEAD | Open PRs | Open issues | Latest GitHub release |")
    print("| --- | --- | ---: | ---: | --- |")
    for name in REPOSITORIES:
        owner_repo = urllib.parse.quote(OWNER + "/" + name, safe="/")
        try:
            metadata = request(f"/repos/{owner_repo}")
            branch = metadata["default_branch"]
            commit = request(f"/repos/{owner_repo}/commits/{urllib.parse.quote(branch, safe='')}")
            head_sha = commit["sha"]
            head = f"[{head_sha[:10]}](https://github.com/{OWNER}/{name}/commit/{head_sha})"
            # GitHub issue listings include PRs: count issue records without pull_request.
            # Pagination avoids silently reporting first-page counts as totals.
            issue_count = 0
            page = 1
            while True:
                issues = request(f"/repos/{owner_repo}/issues?state=open&per_page=100&page={page}")
                issue_count += sum(1 for item in issues if "pull_request" not in item)
                if len(issues) < 100:
                    break
                page += 1
            page = 1
            pr_count = 0
            while True:
                prs = request(f"/repos/{owner_repo}/pulls?state=open&per_page=100&page={page}")
                pr_count += len(prs)
                if len(prs) < 100:
                    break
                page += 1
            try:
                release = request(f"/repos/{owner_repo}/releases/latest").get("tag_name", "unknown")
            except urllib.error.HTTPError as exc:
                if exc.code != 404:
                    raise
                release = "none"
            print(f"| [{name}](https://github.com/{OWNER}/{name}) | {head} | {pr_count} | {issue_count} | {release} |")
        except (KeyError, TypeError, urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError) as exc:
            print(f"| {name} | unknown | unknown | unknown | unknown |")
            print(f"Warning: could not read {name}: {exc}", file=sys.stderr)
            errors += 1

    errors += render_pr_queue("Foundation PRs — exact head SHA and observed PR Actions", FOUNDATION_PRS)
    errors += render_pr_queue("Follow-up PRs — issue intake and CI security", FOLLOWUP_PRS, show_lane=True)
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
