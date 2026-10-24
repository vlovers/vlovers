#!/usr/bin/env python3
"""Restore a previous portfolio history artifact using read-only GitHub Actions API."""

import io
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request
import zipfile


def select_previous_artifact(payload, current_run_id):
    artifacts = payload.get("artifacts", [])
    if not isinstance(artifacts, list):
        raise ValueError("Invalid artifacts payload")
    candidates = [
        a for a in artifacts
        if a.get("name") == "engineering-portfolio-snapshot"
        and not a.get("expired")
        and a.get("workflow_run", {}).get("id") != current_run_id
        and isinstance(a.get("id"), int)
    ]
    return max(candidates, key=lambda a: a.get("created_at", ""), default=None)


def extract_history(data):
    if len(data) > 10_000_000:
        raise ValueError("Artifact archive exceeds limit")
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        members = [m for m in archive.infolist() if m.filename == "portfolio-history.json"]
        if len(members) != 1 or members[0].file_size > 1_000_000:
            raise ValueError("Missing or oversized history in artifact")
        history = json.loads(archive.read(members[0]).decode("utf-8"))
        if not isinstance(history, list):
            raise ValueError("Invalid history data")
        return history


def api(url, token, accept="application/vnd.github+json"):
    request = urllib.request.Request(
        url, headers={"Authorization": "Bearer " + token,
                      "Accept": accept, "X-GitHub-Api-Version": "2022-11-28"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read()


def main():
    repo = os.environ["GITHUB_REPOSITORY"]
    token = os.environ["GITHUB_TOKEN"]
    run_id = int(os.environ["GITHUB_RUN_ID"])
    if not all(repo.split("/")) or repo.count("/") != 1:
        raise ValueError("Invalid repository")
    endpoint = f"https://api.github.com/repos/{repo}/actions/artifacts?per_page=100"
    payload = json.loads(api(endpoint, token))
    artifact = select_previous_artifact(payload, run_id)
    if artifact is None:
        print("No previous snapshot artifact; beginning new history.")
        return
    raw = api(f"https://api.github.com/repos/{repo}/actions/artifacts/{artifact['id']}/zip", token)
    history = extract_history(raw)
    pathlib.Path("portfolio-history.json").write_text(json.dumps(history, indent=2) + "\n")
    print(f"Restored {len(history)} previous history entries.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, urllib.error.URLError, zipfile.BadZipFile) as exc:
        print(f"History restore unavailable: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
