#!/usr/bin/env python3
"""Compare two schema-v1 portfolio snapshots without external dependencies."""

import argparse
import json
import sys


def compare(previous, current):
    for snapshot in (previous, current):
        if not isinstance(snapshot, dict) or snapshot.get("schema_version") != 1:
            raise ValueError("Unsupported snapshot schema")
        if not isinstance(snapshot.get("tracked_prs"), list) or not isinstance(snapshot.get("errors"), list):
            raise ValueError("Malformed snapshot")
    def index(snapshot):
        result = {}
        for item in snapshot["tracked_prs"]:
            if not isinstance(item, dict):
                raise ValueError("Malformed PR")
            repo, number = item.get("repository"), item.get("number")
            if not isinstance(repo, str) or not repo.startswith("vlovers/") or not all(
                c.isascii() and (c.isalnum() or c in "-_") for c in repo.split("/", 1)[1]
            ) or type(number) is not int or number < 1:
                raise ValueError("Invalid PR identity")
            key = (repo, number)
            if key in result:
                raise ValueError("Duplicate PR")
            result[key] = item
        return result
    before, after = index(previous), index(current)
    lines = ["# Portfolio snapshot changes", "",
             "Read-only comparison; not a merge or release decision.", ""]
    if previous["errors"] or current["errors"]:
        lines.append("**Warning:** one or both snapshots have incomplete GitHub data.")
        lines.append("")
    changes = []
    for key in sorted(set(before) | set(after)):
        old, new = before.get(key), after.get(key)
        if old is None or new is None:
            changes.append((key, "tracking", "not tracked" if old is None else "tracked",
                            "tracked" if new is not None else "not tracked"))
            continue
        for field in ("state", "head_sha", "attention", "workflow_observation",
                      "review_observation", "mergeability_observation"):
            left, right = old.get(field), new.get(field)
            if left != right:
                changes.append((key, field, left, right))
    lines.extend(["| PR | Field | Previous | Current |", "| --- | --- | --- | --- |"])
    for (repo, number), field, old, new in changes:
        def safe(value):
            if value is None:
                return "unknown"
            if not isinstance(value, str) or len(value) > 255 or any(
                ord(c) < 32 or c in "|<>" for c in value
            ):
                raise ValueError("Unsafe snapshot value")
            return value
        lines.append(f"| [{repo}#{number}](https://github.com/{repo}/pull/{number}) | "
                     f"{field} | {safe(old)} | {safe(new)} |")
    if not changes:
        lines.append("| — | No observed PR state changes | — | — |")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("previous")
    parser.add_argument("current")
    args = parser.parse_args()
    with open(args.previous, encoding="utf-8") as f:
        previous = json.load(f)
    with open(args.current, encoding="utf-8") as f:
        current = json.load(f)
    print(compare(previous, current), end="")
    return 1 if previous["errors"] or current["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
