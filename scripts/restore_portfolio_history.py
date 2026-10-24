#!/usr/bin/env python3
"""Restore a previous portfolio history artifact using read-only GitHub Actions API."""

import datetime
import io
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request
import zipfile


def select_previous_artifact(payload, current_run_id):
    """Select only well-formed, non-expired artifacts from a different run."""
    if not isinstance(payload, dict) or not isinstance(payload.get("artifacts"), list):
        raise ValueError("Invalid artifacts payload")
    if type(current_run_id) is not int or current_run_id < 1:
        raise ValueError("Invalid current Actions run ID")
    candidates = []
    for artifact in payload["artifacts"]:
        if not isinstance(artifact, dict):
            continue
        if artifact.get("name") != "engineering-portfolio-snapshot":
            continue
        if artifact.get("expired") is not False:
            continue
        workflow_run = artifact.get("workflow_run")
        if not isinstance(workflow_run, dict):
            continue
        previous_run_id = workflow_run.get("id")
        artifact_id = artifact.get("id")
        created_at = artifact.get("created_at")
        if type(previous_run_id) is not int or previous_run_id < 1:
            continue
        if previous_run_id == current_run_id:
            continue
        if type(artifact_id) is not int or artifact_id < 1:
            continue
        if not isinstance(created_at, str) or not created_at:
            continue
        try:
            parsed = datetime.datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except ValueError:
            continue
        candidates.append((parsed, artifact_id, artifact))
    return max(candidates, key=lambda item: (item[0], item[1]))[2] if candidates else None


def extract_history(data):
    if len(data) > 10_000_000:
        raise ValueError("Artifact archive exceeds limit")
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        members = [m for m in archive.infolist() if m.filename == "portfolio-history.json"]
        if len(members) != 1 or members[0].file_size > 1_000_000 or members[0].compress_size > 1_000_000:
            raise ValueError("Missing or oversized history in artifact")
        history = json.loads(archive.read(members[0]).decode("utf-8"))
        if not isinstance(history, list) or len(history) > 365:
            raise ValueError("Invalid history data")
        previous = ""
        for entry in history:
            if not isinstance(entry, dict) or not isinstance(entry.get("observed_at"), str):
                raise ValueError("Invalid history entry")
            timestamp = entry["observed_at"]
            if not timestamp.endswith("Z") or timestamp <= previous:
                raise ValueError("Unordered history entries")
            try:
                datetime.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError as exc:
                raise ValueError("Invalid history timestamp") from exc
            previous = timestamp
        return history


def api(url, token, accept="application/vnd.github+json"):
    request = urllib.request.Request(
        url, headers={"Authorization": "Bearer " + token,
                      "Accept": accept, "X-GitHub-Api-Version": "2022-11-28"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read()


def find_previous_artifact(fetch_page, run_id):
    """Fail closed when no prior artifact can be found within bounded pages."""
    artifact = None
    exhausted = True
    for page in range(1, 6):
        payload = fetch_page(page)
        candidate = select_previous_artifact(payload, run_id)
        if candidate is not None and (artifact is None or
                (candidate.get("created_at") or "", candidate["id"]) >
                (artifact.get("created_at") or "", artifact["id"])):
            artifact = candidate
        artifacts = payload.get("artifacts")
        if not isinstance(artifacts, list) or len(artifacts) > 100:
            raise ValueError("Invalid Actions artifact page")
        if len(artifacts) < 100:
            exhausted = False
            break
    if artifact is None and exhausted:
        raise ValueError("Artifact lookup exceeded five pages; cannot safely start new history")
    return artifact


def main():
    repo = os.environ["GITHUB_REPOSITORY"]
    token = os.environ["GITHUB_TOKEN"]
    run_id = int(os.environ["GITHUB_RUN_ID"])
    if not all(repo.split("/")) or repo.count("/") != 1:
        raise ValueError("Invalid repository")
    endpoint = f"https://api.github.com/repos/{repo}/actions/artifacts?per_page=100"
    artifact = find_previous_artifact(
        lambda page: json.loads(api(f"{endpoint}&page={page}", token)), run_id)
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
