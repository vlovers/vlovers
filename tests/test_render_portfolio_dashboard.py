"""Offline tests for the Markdown dashboard renderer."""

import unittest

from scripts.render_portfolio_dashboard import render


class DashboardTests(unittest.TestCase):
    def test_renders_attention_and_unknown_without_claiming_clearance(self):
        snapshot = {
            "schema_version": 1, "repositories": [{"repository": "vlovers/grid-atlas"}],
            "errors": [],
            "tracked_prs": [{
                "repository": "vlovers/grid-atlas", "number": 272,
                "attention": "ci_failure", "days_since_update": 5,
                "workflow_observation": "failure observed",
            }, {
                "repository": "vlovers/ai-office", "number": 43,
                "attention": "unknown", "days_since_update": None,
                "workflow_observation": None,
            }],
        }
        result = render(snapshot)
        self.assertIn("grid-atlas#272", result)
        self.assertIn("CI failure | 5", result)
        self.assertIn("Unknown | unknown | unknown", result)
        self.assertIn("Never merge or release", result)

    def test_rejects_unsafe_or_invalid_records(self):
        base = {"schema_version": 1, "repositories": [], "errors": [],
                "tracked_prs": [{"repository": "vlovers/grid-atlas", "number": 1,
                                 "attention": "review_needed", "days_since_update": 0,
                                 "workflow_observation": "1/1 observed success"}]}
        for field, value in (("repository", "vlovers/x|bad"), ("number", True),
                             ("attention", "approved"), ("days_since_update", -1),
                             ("workflow_observation", "<script>")):
            snapshot = dict(base, tracked_prs=[dict(base["tracked_prs"][0], **{field: value})])
            with self.subTest(field=field), self.assertRaises(ValueError):
                render(snapshot)



    def test_known_file_overlap_requires_manual_reconciliation(self):
        from scripts.render_portfolio_dashboard import overlap_rows
        rows = overlap_rows([
            {"repository": "vlovers/mutation-boundary", "number": 68, "state": "open"},
            {"repository": "vlovers/mutation-boundary", "number": 69, "state": "open"},
            {"repository": "vlovers/mutation-boundary", "number": 70, "state": "open"},
        ])
        self.assertEqual(len(rows), 2)
        self.assertTrue(any("CONTRIBUTING.md" in row and "manual reconciliation required" in row
                            for row in rows))
        self.assertTrue(any("docs/RELEASING.md" in row for row in rows))

    def test_dependency_order_is_advisory_and_tracks_merged_predecessor(self):
        from scripts.render_portfolio_dashboard import dependency_rows
        rows = dependency_rows([
            {"repository": "vlovers/ai-office", "number": 43, "state": "merged"},
            {"repository": "vlovers/ai-office", "number": 48, "state": "open"},
        ])
        self.assertTrue(any("ai-office#48" in row and "predecessor #43 merged" in row
                            for row in rows))
        self.assertTrue(any("ai-office#49" in row and "await predecessor #48 (open)" in row
                            for row in rows))
        self.assertTrue(any("mutation-boundary#70" in row and "unknown" in row
                            for row in rows))

    def test_marks_incomplete_query_evidence(self):
        snapshot = {"schema_version": 1, "repositories": [], "tracked_prs": [],
                    "errors": [{"target": "vlovers/estima", "error_type": "URLError"}]}
        self.assertIn("Incomplete data", render(snapshot))
