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


def main():
    errors = 0
    print("# Portfolio GitHub status (live read-only query)\n")
    print("| Repository | Open PRs | Open issues | Latest GitHub release |")
    print("| --- | ---: | ---: | --- |")
    for name in REPOSITORIES:
        owner_repo = urllib.parse.quote(OWNER + "/" + name, safe="/")
        try:
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
            print(f"| [{name}](https://github.com/{OWNER}/{name}) | {pr_count} | {issue_count} | {release} |")
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError) as exc:
            print(f"| {name} | unknown | unknown | unknown |")
            print(f"Warning: could not read {name}: {exc}", file=sys.stderr)
            errors += 1
    if errors:
        print(f"\n{errors} repository queries failed; do not treat unknown as zero.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
