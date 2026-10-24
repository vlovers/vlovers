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



    def test_unhashable_attention_and_dependency_state_raise_value_error(self):
        from scripts.render_portfolio_dashboard import dependency_rows
        base = {"schema_version": 1, "repositories": [], "errors": [],
                "tracked_prs": [{"repository": "vlovers/ai-office", "number": 43,
                                 "attention": "review_needed",
                                 "days_since_update": 0,
                                 "workflow_observation": None}]}
        for invalid in ([], {}, ["review_needed"]):
            with self.subTest(attention=invalid), self.assertRaises(ValueError):
                render(dict(base, tracked_prs=[
                    dict(base["tracked_prs"][0], attention=invalid)]))
        for invalid in ([], {}, ["open"]):
            with self.subTest(state=invalid), self.assertRaises(ValueError):
                dependency_rows([{"repository": "vlovers/ai-office",
                                  "number": 43, "state": invalid}])

    def test_overlap_audit_requires_open_pair_and_valid_identity(self):
        from scripts.render_portfolio_dashboard import overlap_rows, dependency_rows
        first = {"repository": "vlovers/mutation-boundary", "number": 68,
                 "state": "open", "head_sha": "d901cc88697a0e3008f866d32b6385f17342d52d"}
        second = {"repository": "vlovers/mutation-boundary", "number": 69,
                  "state": "open", "head_sha": "8b830e3fe622d52bf4d3bdc47803d526c8b95e99"}
        self.assertIn("manual reconciliation required", overlap_rows([first, second])[0])
        self.assertIn("closed PR in pair", overlap_rows([first, dict(second, state="closed")])[0])
        self.assertIn("unknown (PR state", overlap_rows([first, dict(second, state=None)])[0])
        for invalid in (0, -1):
            with self.assertRaises(ValueError):
                overlap_rows([dict(first, number=invalid)])
            with self.assertRaises(ValueError):
                dependency_rows([dict(first, number=invalid)])

    def test_known_file_overlap_requires_manual_reconciliation(self):
        from scripts.render_portfolio_dashboard import overlap_rows
        rows = overlap_rows([
            {"repository": "vlovers/mutation-boundary", "number": 68, "state": "open",
             "head_sha": "d901cc88697a0e3008f866d32b6385f17342d52d"},
            {"repository": "vlovers/mutation-boundary", "number": 69, "state": "open",
             "head_sha": "8b830e3fe622d52bf4d3bdc47803d526c8b95e99"},
            {"repository": "vlovers/mutation-boundary", "number": 70, "state": "open",
             "head_sha": "4e67f8b95c539145dd5516fafdfd2d250f43d9f8"},
        ])
        self.assertEqual(len(rows), 2)
        self.assertTrue(any("CONTRIBUTING.md" in row and "manual reconciliation required" in row
                            for row in rows))
        self.assertTrue(any("docs/RELEASING.md" in row for row in rows))

    def test_stale_overlap_audit_never_claims_reconciliation(self):
        from scripts.render_portfolio_dashboard import overlap_rows
        prs = [
            {"repository": "vlovers/mutation-boundary", "number": 68,
             "state": "open", "head_sha": "a" * 40},
            {"repository": "vlovers/mutation-boundary", "number": 69,
             "state": "open", "head_sha": "8b830e3fe6" + "0" * 30},
        ]
        rows = overlap_rows(prs)
        self.assertIn("stale audit (PR head changed", rows[0])
        snapshot = {"schema_version": 1, "repositories": [], "errors": [],
                    "tracked_prs": [dict(pr, attention="review_needed",
                                        days_since_update=0, workflow_observation=None)
                                    for pr in prs]}
        self.assertIn("Known file overlaps", render(snapshot))
        self.assertIn("stale audit (PR head changed", render(snapshot))

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

    def test_dependency_renderer_rejects_untrusted_state(self):
        from scripts.render_portfolio_dashboard import dependency_rows
        with self.assertRaises(ValueError):
            dependency_rows([{"repository": "vlovers/ai-office", "number": 43,
                              "state": "open|injected"}])

    def test_overlap_audit_rejects_invalid_sha_evidence(self):
        from scripts.render_portfolio_dashboard import overlap_rows
        rows = overlap_rows([
            {"repository": "vlovers/mutation-boundary", "number": 68,
             "state": "open", "head_sha": "not-a-sha"},
            {"repository": "vlovers/mutation-boundary", "number": 69,
             "state": "open", "head_sha": "8b830e3fe622d52bf4d3bd73cf792ad22d584a9"},
        ])
        self.assertIn("unknown (invalid head SHA)", rows[0])

    def test_duplicate_pr_records_fail_closed(self):
        item = {"repository": "vlovers/ai-office", "number": 43,
                "state": "open", "attention": "review_needed",
                "days_since_update": 0, "workflow_observation": None}
        snapshot = {"schema_version": 1, "repositories": [],
                    "errors": [], "tracked_prs": [item, dict(item)]}
        with self.assertRaisesRegex(ValueError, "Duplicate PR"):
            render(snapshot)

    def test_dependency_rows_reject_duplicate_pr_states(self):
        from scripts.render_portfolio_dashboard import dependency_rows
        item = {"repository": "vlovers/ai-office", "number": 43, "state": "open"}
        with self.assertRaisesRegex(ValueError, "Duplicate dependency"):
            dependency_rows([item, dict(item, state="merged")])

    def test_unhashable_pr_identity_fails_with_validation_error(self):
        snapshot = {"schema_version": 1, "repositories": [], "errors": [],
                    "tracked_prs": [{"repository": ["vlovers/ai-office"],
                                     "number": 43, "attention": "unknown"}]}
        with self.assertRaisesRegex(ValueError, "Invalid PR identity"):
            render(snapshot)

    def test_unhashable_dependency_identity_fails_predictably(self):
        from scripts.render_portfolio_dashboard import dependency_rows
        with self.assertRaisesRegex(ValueError, "Invalid dependency PR identity"):
            dependency_rows([{"repository": ["vlovers/ai-office"],
                              "number": 43, "state": "open"}])

    def test_overlap_rows_reject_malformed_and_duplicate_identities(self):
        from scripts.render_portfolio_dashboard import overlap_rows
        with self.assertRaisesRegex(ValueError, "Invalid overlap PR identity"):
            overlap_rows([{"repository": ["vlovers/mutation-boundary"],
                           "number": 68, "state": "open"}])
        item = {"repository": "vlovers/mutation-boundary", "number": 68,
                "state": "open", "head_sha": "a" * 40}
        with self.assertRaisesRegex(ValueError, "Duplicate overlap PR"):
            overlap_rows([item, dict(item, state="merged")])

    def test_marks_incomplete_query_evidence(self):
        snapshot = {"schema_version": 1, "repositories": [], "tracked_prs": [],
                    "errors": [{"target": "vlovers/estima", "error_type": "URLError"}]}
        self.assertIn("Incomplete data", render(snapshot))
