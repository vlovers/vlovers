"""Offline history retention and validation tests."""

import unittest

from scripts.portfolio_history import append_history, summarize


class PortfolioHistoryTests(unittest.TestCase):
    def test_summary_and_bounded_retention(self):
        snapshot = {"schema_version": 1, "repositories": [{}] * 6,
                    "tracked_prs": [
                        {"repository": "vlovers/ai-office", "number": 43, "attention": "ci_pending"},
                        {"repository": "vlovers/estima", "number": 15, "attention": "review_needed"},
                    ], "errors": []}
        first = summarize(snapshot, "2026-10-24T00:00:00Z")
        self.assertEqual(first["attention_counts"], {"ci_pending": 1, "review_needed": 1})
        second = dict(first, observed_at="2026-10-25T00:00:00Z")
        third = dict(first, observed_at="2026-10-26T00:00:00Z")
        self.assertEqual([e["observed_at"] for e in append_history([first, second], third, 2)],
                         ["2026-10-25T00:00:00Z", "2026-10-26T00:00:00Z"])
        self.assertEqual(len(append_history([first], first)), 1)

    def test_rejects_out_of_order_or_duplicate_evidence(self):
        item = {"repository": "vlovers/estima", "number": 15, "attention": "unknown"}
        snapshot = {"schema_version": 1, "repositories": [], "tracked_prs": [item, item],
                    "errors": []}
        with self.assertRaises(ValueError):
            summarize(snapshot, "2026-10-24T00:00:00Z")
        old = {"observed_at": "2026-10-24T00:00:00Z"}
        earlier = {"observed_at": "2026-10-23T00:00:00Z"}
        with self.assertRaises(ValueError):
            append_history([old], earlier)
