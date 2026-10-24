"""Read-only artifact history restoration tests."""

import io
import json
import unittest
import zipfile

from scripts.restore_portfolio_history import extract_history, select_previous_artifact


class RestoreHistoryTests(unittest.TestCase):
    def test_selects_latest_nonexpired_prior_run(self):
        payload = {"artifacts": [
            {"id": 1, "name": "engineering-portfolio-snapshot", "created_at": "2026-10-22", "expired": False, "workflow_run": {"id": 10}},
            {"id": 2, "name": "engineering-portfolio-snapshot", "created_at": "2026-10-23", "expired": False, "workflow_run": {"id": 11}},
            {"id": 3, "name": "engineering-portfolio-snapshot", "created_at": "2026-10-24", "expired": False, "workflow_run": {"id": 12}},
            {"id": 4, "name": "engineering-portfolio-snapshot", "created_at": "2026-10-25", "expired": True, "workflow_run": {"id": 13}},
        ]}
        self.assertEqual(select_previous_artifact(payload, 12)["id"], 2)

    def test_extracts_history_without_unzipping_paths(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("portfolio-history.json", json.dumps([{"observed_at": "2026-10-24T00:00:00Z"}]))
            archive.writestr("../../unsafe.txt", "not extracted")
        self.assertEqual(len(extract_history(buffer.getvalue())), 1)

    def test_rejects_unordered_history(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("portfolio-history.json", json.dumps([
                {"observed_at": "2026-10-25T00:00:00Z"},
                {"observed_at": "2026-10-24T00:00:00Z"},
            ]))
        with self.assertRaises(ValueError):
            extract_history(buffer.getvalue())

    def test_ignores_artifacts_without_workflow_metadata(self):
        payload = {"artifacts": [
            {"id": 7, "name": "engineering-portfolio-snapshot", "expired": False},
            {"id": 8, "name": "engineering-portfolio-snapshot", "expired": False,
             "workflow_run": {"id": 10}, "created_at": "2026-10-24"},
        ]}
        self.assertEqual(select_previous_artifact(payload, 10), None)

    def test_rejects_nonobject_artifact_entries(self):
        with self.assertRaises(ValueError):
            select_previous_artifact({"artifacts": [None]}, 12)

    def test_rejects_boolean_artifact_id(self):
        payload = {"artifacts": [
            {"id": True, "name": "engineering-portfolio-snapshot",
             "expired": False, "workflow_run": {"id": 11}},
        ]}
        self.assertIsNone(select_previous_artifact(payload, 12))

    def test_rejects_invalid_utc_timestamp(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("portfolio-history.json", json.dumps([
                {"observed_at": "2026-99-24T00:00:00Z"},
            ]))
        with self.assertRaises(ValueError):
            extract_history(buffer.getvalue())

    def test_rejects_missing_history(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("unrelated.json", "[]")
        with self.assertRaises(ValueError):
            extract_history(buffer.getvalue())
