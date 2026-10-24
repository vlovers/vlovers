"""Offline regression tests for read-only GitHub portfolio reporting."""

import contextlib
import io
import unittest
from unittest.mock import patch

from scripts import portfolio_status


class PortfolioStatusTests(unittest.TestCase):
    def test_counts_issues_without_pull_requests_and_handles_missing_release(self):
        def fake_request(path):
            if "/actions/runs?" in path:
                return {"total_count": 1, "workflow_runs": [
                    {"head_sha": "a" * 40, "status": "completed", "conclusion": "success"}
                ]}
            if "/pulls/" in path:
                return {"head": {"sha": "a" * 40}, "state": "open", "merged_at": None}
            if path.endswith("/commits/main"):
                return {"sha": "a" * 40}
            if path.endswith("/releases/latest"):
                return {"tag_name": "v1.2.3"}
            if path.endswith("/issues") or "/issues?" in path:
                if "page=1" in path:
                    return [{"number": 1}, {"number": 2, "pull_request": {}}]
                return []
            if "/pulls?" in path:
                return [{"number": 2}]
            if path.endswith("/pulls"):
                return []
            if path.startswith("/repos/") and "?" not in path and "/commits/" not in path:
                return {"default_branch": "main"}
            raise AssertionError(path)

        output = io.StringIO()
        with patch.object(portfolio_status, "request", side_effect=fake_request):
            with contextlib.redirect_stdout(output):
                self.assertEqual(portfolio_status.main(), 0)
        self.assertIn("| [aaaaaaaaaa](https://github.com/vlovers/grid-atlas/commit/" + "a" * 40 + ") | 1 | 1 | v1.2.3 |", output.getvalue())
        self.assertNotIn("Frostline", output.getvalue())

    def test_fails_closed_on_api_errors(self):
        def fail(_path):
            raise TimeoutError("API unavailable")

        with patch.object(portfolio_status, "request", side_effect=fail):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                with contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(portfolio_status.main(), 1)
        self.assertIn("| unknown | unknown | unknown | unknown |", output.getvalue())


    def test_workflow_observation_is_conservative(self):
        sha = "b" * 40
        def run(status="completed", conclusion="success", head_sha=sha):
            return {"head_sha": head_sha, "status": status, "conclusion": conclusion}

        summarize = portfolio_status.summarize_workflow_runs
        self.assertEqual(summarize({"total_count": 1, "workflow_runs": [run()]}, sha),
                         "1/1 observed success")
        self.assertEqual(summarize({"total_count": 1, "workflow_runs": [run("in_progress", None)]}, sha),
                         "pending")
        self.assertEqual(summarize({"total_count": 2, "workflow_runs": [run(), run(conclusion="failure")]}, sha),
                         "failure observed")
        self.assertEqual(summarize({"total_count": 1, "workflow_runs": [run(head_sha="c" * 40)]}, sha),
                         "unknown (no exact-SHA evidence)")
        self.assertEqual(summarize({"total_count": 0, "workflow_runs": []}, sha),
                         "unknown (no exact-SHA evidence)")
        self.assertEqual(summarize({"total_count": 101, "workflow_runs": [run()]}, sha),
                         "unknown (incomplete Actions pagination)")
        self.assertEqual(summarize({"total_count": 1, "workflow_runs": [run(conclusion="skipped")]}, sha),
                         "unknown (non-success conclusion)")

    def test_foundation_status_uses_exact_head_and_does_not_accept_stale_runs(self):
        sha = "a" * 40
        paths = []
        def fake_request(path):
            paths.append(path)
            if path.endswith("/pulls/82"):
                return {"head": {"sha": sha}, "state": "open", "merged_at": None}
            if "/actions/runs?" in path:
                return {"total_count": 1, "workflow_runs": [
                    {"head_sha": "b" * 40, "status": "completed", "conclusion": "success"}
                ]}
            raise AssertionError(path)
        with patch.object(portfolio_status, "request", side_effect=fake_request):
            state, head, ci = portfolio_status.foundation_pr_status("rulewitness", 82)
        self.assertEqual((state, head, ci), ("open", sha, "unknown (no exact-SHA evidence)"))
        self.assertIn("head_sha=" + sha, paths[1])
        self.assertIn("event=pull_request", paths[1])

    def test_foundation_status_rejects_invalid_head_sha(self):
        with patch.object(portfolio_status, "request", return_value={
            "head": {"sha": "invalid"}, "state": "open"
        }):
            with self.assertRaises(ValueError):
                portfolio_status.foundation_pr_status("estima", 13)


if __name__ == "__main__":
    unittest.main()
