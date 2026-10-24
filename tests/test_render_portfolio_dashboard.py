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

    def test_marks_incomplete_query_evidence(self):
        snapshot = {"schema_version": 1, "repositories": [], "tracked_prs": [],
                    "errors": [{"target": "vlovers/estima", "error_type": "URLError"}]}
        self.assertIn("Incomplete data", render(snapshot))
