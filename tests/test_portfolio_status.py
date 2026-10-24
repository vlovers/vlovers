"""Offline regression tests for read-only GitHub portfolio reporting."""

import contextlib
import io
import unittest
from unittest.mock import patch

from scripts import portfolio_status


class PortfolioStatusTests(unittest.TestCase):



    def test_unhashable_review_observation_fails_closed(self):
        base = {"state": "open", "head_sha": "a" * 40,
                "workflow_observation": "1/1 observed success",
                "review_observation": [],
                "mergeability_observation": "mergeable observed (not clearance)"}
        for invalid in ([], {}, None, 1):
            self.assertEqual(portfolio_status.classify_pr_attention(
                dict(base, review_observation=invalid)), "unknown")

    def test_incomplete_pr_identity_cannot_be_review_ready(self):
        classify = portfolio_status.classify_pr_attention
        valid = {"state": "open", "head_sha": "a" * 40,
                 "workflow_observation": "1/1 observed success",
                 "review_observation": "no head-SHA non-author approval observed",
                 "mergeability_observation": "mergeable observed (not clearance)"}
        for record in (None, [], {}, {"state": "open"},
                       dict(valid, head_sha=None),
                       dict(valid, head_sha="not-a-sha"),
                       dict(valid, head_sha=[]),
                       dict(valid, state="unexpected")):
            self.assertEqual(classify(record), "unknown")

    def test_success_counts_must_match_and_state_must_be_scalar(self):
        classify = portfolio_status.classify_pr_attention
        valid = {"state": "open", "head_sha": "a" * 40,
                 "workflow_observation": "1/1 observed success",
                 "review_observation": "no head-SHA non-author approval observed",
                 "mergeability_observation": "mergeable observed (not clearance)"}
        self.assertEqual(classify(valid), "review_needed")
        for workflow in ("1/2 observed success", "2/1 observed success",
                         "01/01 observed success", "0/0 observed success"):
            self.assertEqual(classify(dict(valid, workflow_observation=workflow)),
                             "unknown")
        for state in ([], {}, ["open"]):
            self.assertEqual(classify(dict(valid, state=state)), "unknown")

    def test_unhashable_triage_observations_remain_unknown(self):
        base = {"state": "open", "head_sha": "a" * 40,
                "workflow_observation": "1/1 observed success",
                "review_observation": "no head-SHA non-author approval observed",
                "mergeability_observation": "mergeable observed (not clearance)"}
        for field in ("workflow_observation", "review_observation",
                      "mergeability_observation"):
            for invalid in ([], {}, None):
                result = portfolio_status.classify_pr_attention(
                    dict(base, **{field: invalid}))
                self.assertIn(result, {"unknown", "review_needed"})
                if field != "mergeability_observation":
                    self.assertEqual(result, "unknown")

    def test_pr_inactivity_age_uses_utc_and_rejects_invalid_evidence(self):
        import datetime
        now = datetime.datetime(2026, 10, 24, 12, tzinfo=datetime.timezone.utc)
        self.assertEqual(portfolio_status.pr_age_days("2026-10-20T12:00:00Z", now), 4)
        self.assertEqual(portfolio_status.pr_age_days("2026-10-24T11:59:59+00:00", now), 0)
        for invalid in (None, "2026-10-20", "not-a-date", "2026-10-25T12:00:00Z"):
            with self.assertRaises(ValueError):
                portfolio_status.pr_age_days(invalid, now)

    def test_attention_triage_never_claims_merge_clearance(self):
        base = {"state": "open", "head_sha": "a" * 40,
                "workflow_observation": "1/1 observed success",
                "review_observation": "no head-SHA non-author approval observed",
                "mergeability_observation": "mergeable observed (not clearance)"}
        classify = portfolio_status.classify_pr_attention
        self.assertEqual(classify(base), "review_needed")
        self.assertEqual(classify(dict(base, workflow_observation="failure observed")),
                         "ci_failure")
        self.assertEqual(classify(dict(base, workflow_observation="action required observed")),
                         "action_required")
        self.assertEqual(classify(dict(base, review_observation="changes requested observed (not cleared)")),
                         "changes_requested")
        self.assertEqual(classify(dict(base, mergeability_observation="not mergeable observed (investigate)")),
                         "integration_blocker")
        self.assertEqual(classify(dict(base, workflow_observation="pending")), "ci_pending")
        self.assertEqual(classify(dict(base, workflow_observation="unknown (no exact-SHA evidence)")),
                         "unknown")
        self.assertEqual(classify(dict(base, review_observation=None)), "unknown")
        self.assertEqual(classify(dict(base, review_observation="unexpected review response")), "unknown")
        self.assertEqual(classify(dict(base, review_observation="historical approvals only forged")), "unknown")
        self.assertEqual(classify(dict(base, review_observation="0 head-SHA non-author approval(s) observed (not acceptance)")), "unknown")
        self.assertEqual(classify(dict(base, review_observation="1 head-SHA non-author approval(s) observed (not acceptance) forged")), "unknown")
        self.assertEqual(classify(dict(base, state=None, head_sha=None)), "unknown")
        self.assertEqual(classify(dict(base, state="merged")), "closed")
        self.assertEqual(classify(dict(base, review_observation="1 head-SHA non-author approval(s) observed (not acceptance)")),
                         "review_observed_not_authorized")

    def test_action_required_is_not_misclassified_as_test_failure(self):
        sha = "a" * 40
        response = {"total_count": 1, "workflow_runs": [
            {"head_sha": sha, "status": "completed", "conclusion": "action_required"}
        ]}
        self.assertEqual(portfolio_status.summarize_workflow_runs(response, sha),
                         "action required observed")

    def test_failure_takes_precedence_over_action_required(self):
        sha = "a" * 40
        response = {"total_count": 2, "workflow_runs": [
            {"head_sha": sha, "status": "completed", "conclusion": "action_required"},
            {"head_sha": sha, "status": "completed", "conclusion": "failure"},
        ]}
        self.assertEqual(portfolio_status.summarize_workflow_runs(response, sha),
                         "failure observed")

    def test_dismissed_review_clears_prior_decisive_evidence(self):
        sha = "a" * 40
        def review(state):
            return {"user": {"login": "reviewer", "type": "User"},
                    "state": state, "commit_id": sha}
        summarize = portfolio_status.summarize_review_evidence
        self.assertEqual(summarize([review("APPROVED"), review("DISMISSED")],
                                   sha, "author"),
                         "no head-SHA non-author approval observed")
        self.assertEqual(summarize([review("CHANGES_REQUESTED"), review("DISMISSED")],
                                   sha, "author"),
                         "no head-SHA non-author approval observed")
        self.assertEqual(summarize([review("APPROVED"), review("DISMISSED"),
                                    review("APPROVED")], sha, "author"),
                         "1 head-SHA non-author approval(s) observed (not acceptance)")

    def test_json_snapshot_has_stable_schema_and_exact_sha_observations(self):
        sha = "a" * 40

        def fake_request(path):
            if "/actions/runs?" in path:
                return {"total_count": 1, "workflow_runs": [
                    {"head_sha": sha, "status": "completed", "conclusion": "success"}
                ]}
            if "/reviews?" in path:
                return []
            if "/pulls/" in path:
                return {"head": {"sha": sha}, "state": "open", "merged_at": None,
                        "updated_at": "2026-10-20T12:00:00Z",
                        "user": {"login": "author"}, "mergeable": True}
            if "/commits/main" in path:
                return {"sha": sha}
            if "/releases/latest" in path:
                return {"tag_name": "v1.0.0"}
            if "/issues?" in path or "/pulls?" in path:
                return []
            if path.startswith("/repos/"):
                return {"default_branch": "main"}
            raise AssertionError(path)

        with patch.object(portfolio_status, "request", side_effect=fake_request):
            snapshot = portfolio_status.build_snapshot()
        self.assertEqual(snapshot["schema_version"], 1)
        self.assertEqual(snapshot["errors"], [])
        self.assertEqual(len(snapshot["repositories"]), 6)
        self.assertEqual(len(snapshot["tracked_prs"]), 16)
        self.assertEqual(snapshot["repositories"][0]["head_sha"], sha)
        self.assertEqual(snapshot["tracked_prs"][0]["head_sha"], sha)
        self.assertEqual(snapshot["tracked_prs"][0]["attention"], "review_needed")
        self.assertIsInstance(snapshot["tracked_prs"][0]["days_since_update"], int)
        self.assertEqual(snapshot["tracked_prs"][0]["workflow_observation"],
                         "1/1 observed success")

    def test_json_snapshot_fail_closed_when_github_unavailable(self):
        with patch.object(portfolio_status, "request",
                          side_effect=__import__("urllib").error.URLError("offline")):
            snapshot = portfolio_status.build_snapshot()
        self.assertEqual(len(snapshot["repositories"]), 6)
        self.assertEqual(len(snapshot["tracked_prs"]), 16)
        self.assertEqual(len(snapshot["errors"]), 22)
        self.assertIsNone(snapshot["repositories"][0]["head_sha"])
        self.assertIsNone(snapshot["tracked_prs"][0]["workflow_observation"])

    def test_counts_issues_without_pull_requests_and_handles_missing_release(self):
        def fake_request(path):
            if "/actions/runs?" in path:
                return {"total_count": 1, "workflow_runs": [
                    {"head_sha": "a" * 40, "status": "completed", "conclusion": "success"}
                ]}
            if "/reviews?" in path:
                return []
            if "/compare/" in path:
                return {"status": "diverged", "ahead_by": 2, "behind_by": 1}
            if "/pulls/" in path:
                return {"head": {"sha": "a" * 40}, "base": {"ref": "main"},
                        "state": "open", "merged_at": None,
                        "user": {"login": "author"}}
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
        self.assertIn("## Follow-up PRs — issue intake and CI security", output.getvalue())
        self.assertIn("grid-atlas #272", output.getvalue())
        self.assertIn("estima #15", output.getvalue())

    def test_mergeability_is_observation_not_merge_permission(self):
        self.assertEqual(
            portfolio_status.summarize_mergeability({"mergeable": False}),
            "not mergeable observed (investigate)",
        )
        self.assertEqual(
            portfolio_status.summarize_mergeability({"mergeable": True}),
            "mergeable observed (not clearance)",
        )
        self.assertEqual(
            portfolio_status.summarize_mergeability({"mergeable": None}),
            "unknown (GitHub pending)",
        )
        self.assertEqual(
            portfolio_status.summarize_mergeability({}),
            "unknown (GitHub pending)",
        )
        for invalid in ("false", 0, [], {}):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    portfolio_status.summarize_mergeability({"mergeable": invalid})

    def test_pr_metadata_cache_is_scoped_and_reused_for_drift(self):
        sha = "b" * 40
        calls = []

        def fake_request(path):
            calls.append(path)
            if "/pulls/49" in path and "/reviews?" not in path:
                return {"head": {"sha": sha}, "base": {"ref": "main"},
                        "state": "open", "merged_at": None, "user": {"login": "author"}}
            if "/actions/runs?" in path:
                return {"total_count": 1, "workflow_runs": [
                    {"head_sha": sha, "status": "completed", "conclusion": "success"}
                ]}
            if "/reviews?" in path:
                return []
            if "/compare/" in path:
                return {"status": "diverged", "ahead_by": 17, "behind_by": 15}
            raise AssertionError(path)

        with patch.object(portfolio_status, "request", side_effect=fake_request):
            cache = {}
            self.assertEqual(portfolio_status.foundation_pr_status("ai-office", 49, cache)[0], "open")
            self.assertEqual(portfolio_status.branch_drift_status("ai-office", 49, cache)[1], "main")
            self.assertEqual(
                len([path for path in calls if path.endswith("/pulls/49")]), 1
            )
            # A fresh report gets a fresh cache, not yesterday's PR head.
            portfolio_status.branch_drift_status("ai-office", 49, {})
            self.assertEqual(
                len([path for path in calls if path.endswith("/pulls/49")]), 2
            )

    def test_issue_and_pr_pagination_counts_full_pages_and_filters_prs(self):
        calls = []
        def fake_request(path):
            calls.append(path)
            if path.endswith("page=1"):
                return [{"number": i + 1, **({"pull_request": {}} if i % 2 else {})}
                        for i in range(100)]
            if path.endswith("page=2"):
                return [{"number": 101}]
            raise AssertionError(path)
        with patch.object(portfolio_status, "request", side_effect=fake_request):
            self.assertEqual(portfolio_status.count_open_items("vlovers/grid-atlas", "issues", True), 51)
            self.assertEqual(portfolio_status.count_open_items("vlovers/grid-atlas", "pulls"), 101)
        self.assertEqual(len(calls), 4)

    def test_listing_pagination_fails_closed_on_invalid_or_unbounded_responses(self):
        for bad in (None, {}, [{"number": 1}, None], [{}], [{"number": True}], [{"number": 0}], [{"number": "1"}]):
            with self.subTest(bad=bad):
                with patch.object(portfolio_status, "request", return_value=bad):
                    with self.assertRaises(ValueError):
                        portfolio_status.count_open_items("vlovers/estima", "issues")
        def unbounded_pages(path):
            page = int(path.rsplit("page=", 1)[1])
            return [{"number": (page - 1) * 100 + i + 1} for i in range(100)]
        with patch.object(portfolio_status, "request", side_effect=unbounded_pages) as fetch:
            with self.assertRaisesRegex(ValueError, "pagination exceeded"):
                portfolio_status.count_open_items("vlovers/estima", "pulls")
        self.assertEqual(fetch.call_count, 20)

    def test_listing_pagination_rejects_duplicate_ids_across_pages(self):
        def duplicate_page(path):
            if path.endswith("page=1"):
                return [{"number": i + 1} for i in range(100)]
            return [{"number": 100}, {"number": 101}]
        with patch.object(portfolio_status, "request", side_effect=duplicate_page):
            with self.assertRaisesRegex(ValueError, "Duplicate issues item"):
                portfolio_status.count_open_items("vlovers/estima", "issues")

    def test_listing_rejects_oversized_pages_and_invalid_pull_request_markers(self):
        for items in (
            [{"number": i + 1} for i in range(101)],
            [{"number": 1, "pull_request": None}],
            [{"number": 1, "pull_request": "not an object"}],
        ):
            with self.subTest(items=items[:2]):
                with patch.object(portfolio_status, "request", return_value=items):
                    with self.assertRaisesRegex(ValueError, "Malformed issues listing"):
                        portfolio_status.count_open_items("vlovers/estima", "issues", True)

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

    def test_workflow_observation_rejects_invalid_status_and_conclusion_types(self):
        sha = "a" * 40
        summarize = portfolio_status.summarize_workflow_runs
        for status, conclusion in (
            (None, "success"),
            (["completed"], "success"),
            ("unknown-status", "success"),
            ("completed", []),
            ("completed", {"unexpected": True}),
            ("completed", "unknown-conclusion"),
        ):
            with self.subTest(status=status, conclusion=conclusion):
                with self.assertRaises(ValueError):
                    summarize({"total_count": 1, "workflow_runs": [
                        {"head_sha": sha, "status": status, "conclusion": conclusion}
                    ]}, sha)

    def test_foundation_status_uses_exact_head_and_does_not_accept_stale_runs(self):
        sha = "a" * 40
        paths = []
        def fake_request(path):
            paths.append(path)
            if path.endswith("/pulls/82"):
                return {"head": {"sha": sha}, "state": "open", "merged_at": None,
                        "user": {"login": "author"}}
            if "/reviews?" in path:
                return []
            if "/actions/runs?" in path:
                return {"total_count": 1, "workflow_runs": [
                    {"head_sha": "b" * 40, "status": "completed", "conclusion": "success"}
                ]}
            raise AssertionError(path)
        with patch.object(portfolio_status, "request", side_effect=fake_request):
            state, head, ci, review, mergeability = portfolio_status.foundation_pr_status("rulewitness", 82)
        self.assertEqual((state, head, ci, review),
                         ("open", sha, "unknown (no exact-SHA evidence)",
                          "no head-SHA non-author approval observed"))
        self.assertEqual(mergeability, "unknown (GitHub pending)")
        self.assertIn("head_sha=" + sha, paths[1])
        self.assertIn("event=pull_request", paths[1])

    def test_foundation_status_rejects_invalid_head_sha(self):
        with patch.object(portfolio_status, "request", return_value={
            "head": {"sha": "invalid"}, "state": "open"
        }):
            with self.assertRaises(ValueError):
                portfolio_status.foundation_pr_status("estima", 13)


    def test_review_observation_requires_current_head_and_non_author(self):
        sha = "a" * 40
        def review(login, state="APPROVED", commit=None, kind="User"):
            return {"user": {"login": login, "type": kind}, "state": state,
                    "commit_id": commit or sha}
        summarize = portfolio_status.summarize_review_evidence
        self.assertEqual(summarize([], sha, "author"),
                         "no head-SHA non-author approval observed")
        self.assertEqual(summarize([review("author"), review("ci[bot]", kind="Bot")],
                                   sha, "author"),
                         "no head-SHA non-author approval observed")
        self.assertEqual(summarize([review("reviewer", commit="b" * 40)],
                                   sha, "author"),
                         "historical approvals only (not head-SHA)")
        self.assertEqual(summarize([review("reviewer")], sha, "author"),
                         "1 head-SHA non-author approval(s) observed (not acceptance)")
        self.assertEqual(summarize([review("reviewer"),
                                    review("reviewer", "DISMISSED")], sha, "author"),
                         "no head-SHA non-author approval observed")
        self.assertEqual(summarize([review("reviewer"),
                                    review("second", "CHANGES_REQUESTED")], sha, "author"),
                         "changes requested observed (not cleared)")
        self.assertEqual(summarize([review("reviewer", "CHANGES_REQUESTED"),
                                    review("reviewer")], sha, "author"),
                         "1 head-SHA non-author approval(s) observed (not acceptance)")
        with self.assertRaises(ValueError):
            summarize([{"state": "APPROVED"}], sha, "author")
        with self.assertRaises(ValueError):
            summarize([], sha, None)

    def test_review_pagination_never_truncates_approvals(self):
        calls = []
        def fake_request(path):
            calls.append(path)
            if path.endswith("&page=1"):
                return [{"user": {"login": f"reviewer-{i}"}, "state": "COMMENTED"}
                        for i in range(100)]
            if path.endswith("&page=2"):
                return [{"user": {"login": "reviewer"}, "state": "APPROVED",
                         "commit_id": "a" * 40}]
            raise AssertionError(path)
        with patch.object(portfolio_status, "request", side_effect=fake_request):
            reviews = portfolio_status.fetch_pr_reviews("vlovers/rulewitness", 82)
        self.assertEqual(len(reviews), 101)
        self.assertEqual(len(calls), 2)
        with patch.object(portfolio_status, "request", return_value={"not": "a list"}):
            with self.assertRaises(ValueError):
                portfolio_status.fetch_pr_reviews("vlovers/rulewitness", 82)

    def test_report_fails_closed_when_review_lookup_fails(self):
        sha = "a" * 40
        def fake_request(path):
            if path.endswith("/pulls/82"):
                return {"head": {"sha": sha}, "state": "open",
                        "user": {"login": "author"}}
            if "/actions/runs?" in path:
                return {"total_count": 1, "workflow_runs": [
                    {"head_sha": sha, "status": "completed", "conclusion": "success"}]}
            if "/reviews?" in path:
                raise TimeoutError("Review API unavailable")
            raise AssertionError(path)
        with patch.object(portfolio_status, "request", side_effect=fake_request):
            with self.assertRaises(TimeoutError):
                portfolio_status.foundation_pr_status("rulewitness", 82)


    def test_followup_queue_covers_existing_intake_and_ci_security_prs(self):
        self.assertEqual(
            {(name, number, lane) for name, number, lane in portfolio_status.FOLLOWUP_PRS},
            {
                ("grid-atlas", 271, "issue intake"),
                ("grid-atlas", 272, "CI security"),
                ("ai-office", 48, "issue intake"),
                ("ai-office", 49, "CI security"),
                ("rulewitness", 83, "issue intake"),
                ("mutation-boundary", 69, "issue intake"),
                ("mutation-boundary", 70, "CI security"),
                ("estima", 14, "issue intake"),
                ("estima", 15, "CI security"),
            },
        )
        self.assertNotIn("frostline", {name for name, _, _ in portfolio_status.FOLLOWUP_PRS})

    def test_followup_table_shows_exact_head_and_unknown_on_failed_lookup(self):
        sha = "c" * 40
        output = io.StringIO()
        with patch.object(portfolio_status, "foundation_pr_status", side_effect=[
            ("open", sha, "1/1 observed success", "no head-SHA non-author approval observed", "mergeable observed (not clearance)"),
            TimeoutError("GitHub unavailable"),
        ]):
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(io.StringIO()):
                failures = portfolio_status.render_pr_queue(
                    "Follow-up checks",
                    (("grid-atlas", 272, "CI security"), ("estima", 15, "CI security")),
                    show_lane=True,
                )
        self.assertEqual(failures, 1)
        self.assertIn("| Lane | State |", output.getvalue())
        self.assertIn("| open | `cccccccccccc` | 1/1 observed success |", output.getvalue())
        self.assertIn("estima #15", output.getvalue())
        self.assertIn("| unknown | unknown | unknown | unknown |", output.getvalue())

    def test_main_fails_closed_when_followup_review_unavailable(self):
        with patch.object(portfolio_status, "REPOSITORIES", ()), \
             patch.object(portfolio_status, "FOUNDATION_PRS", ()), \
             patch.object(portfolio_status, "FOLLOWUP_PRS", (("estima", 15, "CI security"),)), \
             patch.object(portfolio_status, "foundation_pr_status", side_effect=TimeoutError("review unavailable")):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                with contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(portfolio_status.main(), 1)
        self.assertIn("estima #15", output.getvalue())
        self.assertIn("| unknown | unknown | unknown | unknown |", output.getvalue())

    def test_branch_drift_tracks_all_unmerged_engineering_prs(self):
        expected = {
            (name, number)
            for name, number, *_ in (
                *portfolio_status.FOUNDATION_PRS,
                *portfolio_status.FOLLOWUP_PRS,
            )
            if (name, number) != ("grid-atlas", 268)
        }
        self.assertEqual(set(portfolio_status.BRANCH_DRIFT_PRS), expected)
        self.assertEqual(len(portfolio_status.BRANCH_DRIFT_PRS), len(expected))
        self.assertIn(("estima", 15), expected)
        self.assertIn(("last-chapter", 5), expected)
        self.assertIn("last-chapter", portfolio_status.REPOSITORIES)
        self.assertIn(("mutation-boundary", 70), expected)
        self.assertNotIn(("grid-atlas", 268), expected)

    def test_branch_divergence_uses_live_base_ref_not_historical_base_sha(self):
        sha = "a" * 40
        paths = []
        def fake_request(path):
            paths.append(path)
            if path.endswith("/pulls/43"):
                return {"head": {"sha": sha}, "base": {"ref": "main", "sha": "b" * 40}}
            if "/compare/" in path:
                return {"status": "diverged", "ahead_by": 16, "behind_by": 13}
            raise AssertionError(path)
        with patch.object(portfolio_status, "request", side_effect=fake_request):
            self.assertEqual(
                portfolio_status.branch_drift_status("ai-office", 43),
                (sha, "main", "base-only 16; PR-only 13 (diverged)"),
            )
        self.assertEqual(paths[-1], "/repos/vlovers/ai-office/compare/" + sha + "...main")
        self.assertNotIn("b" * 40, paths[-1])

    def test_branch_divergence_uses_actual_develop_target_for_estima(self):
        sha = "c" * 40
        paths = []
        def fake_request(path):
            paths.append(path)
            if path.endswith("/pulls/15"):
                return {"head": {"sha": sha}, "base": {"ref": "develop"}}
            if "/compare/" in path:
                return {"status": "ahead", "ahead_by": 3, "behind_by": 0}
            raise AssertionError(path)
        with patch.object(portfolio_status, "request", side_effect=fake_request):
            self.assertEqual(
                portfolio_status.branch_drift_status("estima", 15),
                (sha, "develop", "base-only 3; PR-only 0 (ahead)"),
            )
        self.assertEqual(paths[-1], "/repos/vlovers/estima/compare/" + sha + "...develop")

    def test_branch_divergence_counts_direction_and_equal_heads(self):
        summarize = portfolio_status.summarize_branch_divergence
        self.assertEqual(summarize({"status": "ahead", "ahead_by": 2, "behind_by": 0}),
                         "base-only 2; PR-only 0 (ahead)")
        self.assertEqual(summarize({"status": "behind", "ahead_by": 0, "behind_by": 5}),
                         "base-only 0; PR-only 5 (behind)")
        self.assertEqual(summarize({"status": "identical", "ahead_by": 0, "behind_by": 0}),
                         "base-only 0; PR-only 0 (identical)")

    def test_branch_divergence_rejects_malformed_and_boolean_counts(self):
        summarize = portfolio_status.summarize_branch_divergence
        for bad in (None, {}, {"status": "diverged", "ahead_by": True, "behind_by": 1},
                    {"status": "diverged", "ahead_by": -1, "behind_by": 1},
                    {"status": "diverged", "ahead_by": 2, "behind_by": "3"},
                    {"status": "unexpected", "ahead_by": 2, "behind_by": 3}):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    summarize(bad)

    def test_branch_divergence_rejects_invalid_base_and_head(self):
        with patch.object(portfolio_status, "request", return_value={
            "head": {"sha": "a" * 40}, "base": {"ref": "refs/heads/main"}
        }):
            with self.assertRaises(ValueError):
                portfolio_status.branch_drift_status("ai-office", 43)
        with patch.object(portfolio_status, "request", return_value={
            "head": {"sha": "not-a-sha"}, "base": {"ref": "main"}
        }):
            with self.assertRaises(ValueError):
                portfolio_status.branch_drift_status("ai-office", 43)

    def test_branch_divergence_table_fails_closed_on_compare_error(self):
        with patch.object(portfolio_status, "BRANCH_DRIFT_PRS", (("ai-office", 43),)), \
             patch.object(portfolio_status, "branch_drift_status", side_effect=TimeoutError("compare unavailable")):
            with contextlib.redirect_stdout(io.StringIO()) as output, \
                 contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(portfolio_status.render_branch_drift_queue(), 1)
        self.assertIn("| unknown | unknown | unknown |", output.getvalue())

    def test_sha_validation_rejects_non_string_and_invalid_commit_ids(self):
        validate = portfolio_status.validate_sha
        self.assertEqual(validate("a" * 40), "a" * 40)
        self.assertEqual(validate("A" * 40), "A" * 40)
        for invalid in (None, True, 123, "a" * 39, "a" * 41, "g" * 40,
                        "a" * 40 + "\n", ["a" * 40]):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                validate(invalid)

    def test_release_metadata_cannot_inject_markdown_rows(self):
        sanitize = portfolio_status.safe_markdown_cell
        self.assertEqual(sanitize("v1.2.3|untrusted"), r"v1.2.3\|untrusted")
        self.assertEqual(sanitize("v1" + chr(92) + "|fake"), "v1" + chr(92) * 3 + "|fake")
        for invalid in (None, "", True, 123, "v1\n| forged | pass |",
                        "v1\rforged", "x" * 256):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                sanitize(invalid)

    def test_reviews_require_explicit_account_type_to_prevent_bot_approval(self):
        sha = "a" * 40
        summarize = portfolio_status.summarize_review_evidence
        for kind in ("Bot", "Organization", "Mannequin"):
            review = {"user": {"login": "other", "type": kind},
                      "state": "APPROVED", "commit_id": sha}
            self.assertEqual(summarize([review], sha, "author"),
                             "no head-SHA non-author approval observed")
        for kind in (None, "Unexpected", 42):
            review = {"user": {"login": "other", "type": kind},
                      "state": "APPROVED", "commit_id": sha}
            with self.assertRaises(ValueError):
                summarize([review], sha, "author")
        with self.assertRaises(ValueError):
            summarize([None], sha, "author")

    def test_reviews_reject_missing_states_and_malformed_author(self):
        sha = "a" * 40
        valid = {"user": {"login": "reviewer", "type": "User"},
                 "state": "APPROVED", "commit_id": sha}
        summarize = portfolio_status.summarize_review_evidence
        for bad in ({**valid, "state": None}, {**valid, "state": []},
                    {**valid, "state": "APPROVE"}):
            with self.assertRaises(ValueError):
                summarize([bad], sha, "author")
        for author in (None, True, 3, [], ""):
            with self.assertRaises(ValueError):
                summarize([valid], sha, author)
        with self.assertRaises(ValueError):
            summarize([valid], "invalid", "author")

    def test_workflow_total_count_boolean_is_not_accepted_as_complete(self):
        sha = "a" * 40
        with self.assertRaises(ValueError):
            portfolio_status.summarize_workflow_runs({
                "total_count": True, "workflow_runs": [
                    {"head_sha": sha, "status": "completed", "conclusion": "success"}
                ]
            }, sha)

    def test_repository_metadata_validation_fails_closed(self):
        def fake_request(path):
            if path == "/repos/vlovers/estima":
                return {"default_branch": "develop"}
            if path.endswith("/commits/develop"):
                return {"sha": "invalid"}
            raise AssertionError(path)
        with patch.object(portfolio_status, "REPOSITORIES", ("estima",)), \
             patch.object(portfolio_status, "FOUNDATION_PRS", ()), \
             patch.object(portfolio_status, "FOLLOWUP_PRS", ()), \
             patch.object(portfolio_status, "BRANCH_DRIFT_PRS", ()), \
             patch.object(portfolio_status, "request", side_effect=fake_request):
            with contextlib.redirect_stdout(io.StringIO()) as output, \
                 contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(portfolio_status.main(), 1)
        self.assertIn("| estima | unknown | unknown | unknown | unknown |", output.getvalue())

    def test_rejects_malformed_workflow_metadata_instead_of_reporting_success(self):
        sha = "a" * 40
        summarize = portfolio_status.summarize_workflow_runs
        for malformed in (None, {}, {"workflow_runs": [], "total_count": -1},
                          {"workflow_runs": {}, "total_count": 0},
                          {"workflow_runs": [None], "total_count": 1},
                          {"workflow_runs": [], "total_count": "0"}):
            with self.subTest(malformed=malformed):
                with self.assertRaises(ValueError):
                    summarize(malformed, sha)


if __name__ == "__main__":
    unittest.main()
