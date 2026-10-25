"""Offline snapshot-diff regression tests."""

import unittest

from scripts.compare_portfolio_snapshots import compare


class SnapshotDiffTests(unittest.TestCase):
    def test_reports_changed_head_and_attention(self):
        old = {"schema_version": 1, "errors": [], "tracked_prs": [{
            "repository": "vlovers/estima", "number": 15, "state": "open",
            "head_sha": "a" * 40, "attention": "ci_pending",
        }]}
        new = {"schema_version": 1, "errors": [], "tracked_prs": [{
            "repository": "vlovers/estima", "number": 15, "state": "open",
            "head_sha": "b" * 40, "attention": "review_needed",
        }]}
        output = compare(old, new)
        self.assertIn("estima#15", output)
        self.assertIn("head_sha", output)
        self.assertIn("attention", output)
        self.assertIn("not a merge or release decision", output)

    def test_missing_data_does_not_look_complete(self):
        old = {"schema_version": 1, "errors": [{"target": "vlovers/estima"}],
               "tracked_prs": []}
        new = {"schema_version": 1, "errors": [], "tracked_prs": []}
        self.assertIn("incomplete GitHub data", compare(old, new))

    def test_rejects_duplicate_prs(self):
        item = {"repository": "vlovers/estima", "number": 15}
        snapshot = {"schema_version": 1, "errors": [], "tracked_prs": [item, item]}
        with self.assertRaises(ValueError):
            compare(snapshot, snapshot)
