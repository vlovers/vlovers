#!/usr/bin/env python3
"""Render a safe, deterministic Markdown dashboard from a portfolio JSON snapshot."""

import argparse
import json
import sys

ATTENTION = {
    "ci_failure": "CI failure",
    "changes_requested": "Changes requested",
    "integration_blocker": "Integration blocker",
    "ci_pending": "CI pending",
    "review_needed": "Review needed",
    "review_observed_not_authorized": "Review observed (not approved for merge)",
    "unknown": "Unknown",
    "closed": "Closed",
}


def render(snapshot):
    if not isinstance(snapshot, dict) or snapshot.get("schema_version") != 1:
        raise ValueError("Unsupported snapshot schema")
    prs = snapshot.get("tracked_prs")
    repos = snapshot.get("repositories")
    errors = snapshot.get("errors")
    if not isinstance(prs, list) or not isinstance(repos, list) or not isinstance(errors, list):
        raise ValueError("Malformed snapshot collections")
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
