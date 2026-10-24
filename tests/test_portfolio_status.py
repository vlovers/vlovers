"""Offline regression tests for read-only GitHub portfolio reporting."""

import contextlib
import io
import unittest
from unittest.mock import patch

from scripts import portfolio_status


class PortfolioStatusTests(unittest.TestCase):
    def test_counts_issues_without_pull_requests_and_handles_missing_release(self):
        def fake_request(path):
            if "/issues?" in path:
                if "page=1" in path:
                    return [{"number": 1}, {"number": 2, "pull_request": {}}]
                return []
            if "/pulls?" in path:
                return [{"number": 2}]
            if "/releases/latest" in path:
                return {"tag_name": "v1.2.3"}
            raise AssertionError(path)

        output = io.StringIO()
        with patch.object(portfolio_status, "request", side_effect=fake_request):
            with contextlib.redirect_stdout(output):
                self.assertEqual(portfolio_status.main(), 0)
        self.assertIn("| 1 | 1 | v1.2.3 |", output.getvalue())
        self.assertNotIn("Frostline", output.getvalue())

    def test_fails_closed_on_api_errors(self):
        def fail(_path):
            raise TimeoutError("API unavailable")

        with patch.object(portfolio_status, "request", side_effect=fail):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                with contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(portfolio_status.main(), 1)
        self.assertIn("| unknown | unknown | unknown |", output.getvalue())


if __name__ == "__main__":
    unittest.main()
