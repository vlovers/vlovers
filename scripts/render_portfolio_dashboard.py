#!/usr/bin/env python3
"""Render a safe, deterministic Markdown dashboard from a portfolio JSON snapshot."""

import argparse
import json
import sys

ATTENTION = {
    "ci_failure": "CI failure",
    "action_required": "Actions approval/action required",
    "changes_requested": "Changes requested",
    "integration_blocker": "Integration blocker",
    "ci_pending": "CI pending",
    "review_needed": "Review needed",
    "review_observed_not_authorized": "Review observed (not approved for merge)",
    "unknown": "Unknown",
    "closed": "Closed",
}



# Explicit engineering review order; not inferred from GitHub mergeability.
DEPENDENCY_CHAINS = (
    ("vlovers/ai-office", (43, 48, 49)),
    ("vlovers/rulewitness", (82, 83)),
    ("vlovers/mutation-boundary", (68, 69, 70)),
    ("vlovers/estima", (13, 14, 15)),
    ("vlovers/grid-atlas", (271, 272)),
)


def dependency_rows(prs):
    """Show known integration order without claiming a PR is safe to merge."""
    states = {}
    for p in prs:
        if not isinstance(p, dict):
            raise ValueError("Malformed dependency PR record")
        state = p.get("state")
        if state is not None and state not in {"open", "closed", "merged"}:
            raise ValueError("Invalid dependency PR state")
        states[(p.get("repository"), p.get("number"))] = state
    rows = []
    for repo, numbers in DEPENDENCY_CHAINS:
        for index, number in enumerate(numbers):
            predecessor = numbers[index - 1] if index else None
            prior_state = states.get((repo, predecessor)) if predecessor else None
            if predecessor is None:
                dependency = "first in lane"
            elif prior_state == "merged":
                dependency = f"predecessor #{predecessor} merged (recheck head CI)"
            elif prior_state is None:
                dependency = f"predecessor #{predecessor} unknown"
            else:
                dependency = f"await predecessor #{predecessor} ({prior_state})"
            rows.append(f"| [{repo}#{number}](https://github.com/{repo}/pull/{number}) | {dependency} |")
    return rows




# Explicitly audited changed-file overlaps; update after PR head changes.
KNOWN_FILE_OVERLAPS = (
    ("vlovers/mutation-boundary", 68, 69, ("CONTRIBUTING.md",),
     "d901cc88697a0e3008f866d32b6385f17342d52d",
     "8b830e3fe622d52bf4d3bdc47803d526c8b95e99"),
    ("vlovers/mutation-boundary", 68, 70, ("README.md", "docs/RELEASING.md"),
     "d901cc88697a0e3008f866d32b6385f17342d52d",
     "4e67f8b95c539145dd5516fafdfd2d250f43d9f8"),
)


def overlap_rows(prs):
    index = {(p.get("repository"), p.get("number")): p for p in prs
             if isinstance(p, dict)}
    rows = []
    for repo, first, second, paths, audited_first, audited_second in KNOWN_FILE_OVERLAPS:
        a, b = index.get((repo, first)), index.get((repo, second))
        if not a or not b:
            status = "unknown (PR missing from snapshot)"
        elif a.get("state") == "merged" or b.get("state") == "merged":
            status = "re-audit against new base"
        elif not isinstance(a.get("head_sha"), str) or not isinstance(b.get("head_sha"), str):
            status = "unknown (head SHA unavailable)"
        elif any(len(sha) != 40 or any(char not in "0123456789abcdefABCDEF" for char in sha)
                 for sha in (a["head_sha"], b["head_sha"])):
            status = "unknown (invalid head SHA)"
        elif a["head_sha"] != audited_first or b["head_sha"] != audited_second:
            status = "stale audit (PR head changed; re-audit files)"
        else:
            status = "manual reconciliation required (heads match audit)"
        safe_paths = ", ".join(paths)
        rows.append(f"| {repo} #{first} / #{second} | {safe_paths} | {status} |")
    return rows



def render(snapshot):
    if not isinstance(snapshot, dict) or snapshot.get("schema_version") != 1:
        raise ValueError("Unsupported snapshot schema")
    prs = snapshot.get("tracked_prs")
    repos = snapshot.get("repositories")
    errors = snapshot.get("errors")
    if not isinstance(prs, list) or not isinstance(repos, list) or not isinstance(errors, list):
        raise ValueError("Malformed snapshot collections")
    seen_prs = set()
    for item in prs:
        if not isinstance(item, dict):
            raise ValueError("Malformed PR record")
        key = (item.get("repository"), item.get("number"))
        if key in seen_prs:
            raise ValueError("Duplicate PR in snapshot")
        seen_prs.add(key)
    lines = ["# Engineering portfolio dashboard", "",
             "Read-only GitHub observations. **Never merge or release based on this report.**", "",
             f"Repositories: {len(repos)} · Tracked PRs: {len(prs)} · Query errors: {len(errors)}", "",
             "| PR | Attention | Days since last update | CI observation |",
             "| --- | --- | ---: | --- |"]
    for item in prs:
        if not isinstance(item, dict):
            raise ValueError("Malformed PR record")
        repo, number, attention = item.get("repository"), item.get("number"), item.get("attention")
        if not isinstance(repo, str) or not repo.startswith("vlovers/") or not all(
            c.isascii() and (c.isalnum() or c in "-_") for c in repo.split("/", 1)[1]
        ):
            raise ValueError("Invalid repository")
        if type(number) is not int or number < 1 or attention not in ATTENTION:
            raise ValueError("Invalid PR identifier or attention")
        age = item.get("days_since_update")
        if age is not None and (type(age) is not int or age < 0):
            raise ValueError("Invalid inactivity age")
        ci = item.get("workflow_observation")
        if ci is not None and (not isinstance(ci, str) or len(ci) > 120 or any(
            ord(c) < 32 or c in "|<>" for c in ci
        )):
            raise ValueError("Unsafe CI observation")
        label = f"[{repo}#{number}](https://github.com/{repo}/pull/{number})"
        lines.append(f"| {label} | {ATTENTION[attention]} | {age if age is not None else 'unknown'} | {ci or 'unknown'} |")
    lines.extend(["", "## Integration dependencies (advisory)", "",
                  "| PR | Dependency observation |", "| --- | --- |"])
    lines.extend(dependency_rows(prs))
    lines.extend(["", "## Known file overlaps (audit snapshot)", "",
                  "| PR pair | Files | Required follow-up |", "| --- | --- | --- |"])
    lines.extend(overlap_rows(prs))
    if errors:
        lines.extend(["", "**Incomplete data:** one or more GitHub queries failed. Missing observations are unknown."])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot", help="Path to JSON snapshot")
    args = parser.parse_args()
    with open(args.snapshot, encoding="utf-8") as source:
        snapshot = json.load(source)
    print(render(snapshot), end="")
    return 1 if snapshot["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
