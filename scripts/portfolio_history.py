#!/usr/bin/env python3
"""Build a bounded, append-only local history from saved portfolio snapshots."""

import argparse
import datetime
import json
import pathlib
import sys


def summarize(snapshot, observed_at):
    if not isinstance(snapshot, dict) or snapshot.get("schema_version") != 1:
        raise ValueError("Unsupported snapshot schema")
    prs, repos, errors = (snapshot.get(key) for key in ("tracked_prs", "repositories", "errors"))
    if not all(isinstance(items, list) for items in (prs, repos, errors)):
        raise ValueError("Malformed snapshot")
    if not isinstance(observed_at, str) or not observed_at.endswith("Z"):
        raise ValueError("Timestamp must be UTC")
    datetime.datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
    counts = {}
    identities = set()
    for pr in prs:
        if not isinstance(pr, dict) or not isinstance(pr.get("attention"), str):
            raise ValueError("Malformed PR attention")
        identity = (pr.get("repository"), pr.get("number"))
        if not isinstance(identity[0], str) or type(identity[1]) is not int:
            raise ValueError("Malformed PR identity")
        if identity in identities:
            raise ValueError("Duplicate PR")
        identities.add(identity)
        attention = pr["attention"]
        if attention not in {
            "ci_failure", "action_required", "changes_requested", "integration_blocker", "ci_pending",
            "review_needed", "review_observed_not_authorized", "unknown", "closed"
        }:
            raise ValueError("Unexpected attention category")
        counts[attention] = counts.get(attention, 0) + 1
    return {"observed_at": observed_at, "repositories": len(repos),
            "tracked_prs": len(prs), "query_errors": len(errors),
            "attention_counts": dict(sorted(counts.items()))}


def append_history(history, summary, max_entries=90):
    if not isinstance(history, list) or not isinstance(summary, dict):
        raise ValueError("Malformed history")
    if type(max_entries) is not int or max_entries < 1 or max_entries > 365:
        raise ValueError("Invalid retention")
    timestamp = summary.get("observed_at")
    if not isinstance(timestamp, str) or not timestamp.endswith("Z"):
        raise ValueError("Invalid summary timestamp")
    for entry in history:
        if not isinstance(entry, dict) or not isinstance(entry.get("observed_at"), str):
            raise ValueError("Malformed history entry")
    if history and timestamp < history[-1]["observed_at"]:
        raise ValueError("Out-of-order history")
    result = [entry for entry in history if entry["observed_at"] != timestamp]
    result.append(summary)
    return result[-max_entries:]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot")
    parser.add_argument("--history", default="portfolio-history.json")
    parser.add_argument("--max-entries", type=int, default=90)
    args = parser.parse_args()
    snapshot = json.loads(pathlib.Path(args.snapshot).read_text(encoding="utf-8"))
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    path = pathlib.Path(args.history)
    history = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    updated = append_history(history, summarize(snapshot, now), args.max_entries)
    path.write_text(json.dumps(updated, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 1 if snapshot["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
