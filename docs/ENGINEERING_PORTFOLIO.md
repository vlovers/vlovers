# Engineering portfolio — active projects

**Engineering normalization:** see the [verified rollout audit, gap matrix and cleanup gates](ENGINEERING_ROLLOUT_AUDIT.md), the [cross-repository engineering work queue](ENGINEERING_WORK_QUEUE.md), and the [owner-ready branch protection setup guide](BRANCH_RULESET_SETUP.md).

**Machine-readable report:** run `python3 scripts/portfolio_status.py --format json` to emit schema v1 with six repository records, tracked PR observations and explicit query errors. JSON mode exits nonzero if any query failed. This is read-only observational data, not merge clearance; do not commit API tokens or interpret missing values as passing checks. The default output remains Markdown. Generate a readable dashboard with `python3 scripts/render_portfolio_dashboard.py portfolio-snapshot.json > portfolio-dashboard.md`. Compare two downloaded snapshots with `python3 scripts/compare_portfolio_snapshots.py previous.json current.json`; this comparison reports observed changes and flags incomplete API evidence. The scheduled workflow stores current JSON and Markdown artifacts, not a permanent history database; retaining snapshots is required for cross-day comparisons.\n\n**Automation (proposed):** [Portfolio snapshot workflow](../.github/workflows/portfolio-snapshot.yml) runs daily at 06:17 UTC and supports manual dispatch **after this PR is merged to the default branch**. It uses a read-only token, uploads a JSON artifact retained for 14 days, and fails the run if GitHub queries are incomplete. The JSON `attention` field is triage only (CI failure, changes requested, integration blocker, pending, review needed, unknown); it never authorizes merging. GitHub scheduled workflows may be delayed.\n\n**History:** `python3 scripts/portfolio_history.py portfolio-snapshot.json --history portfolio-history.json` creates or appends a bounded (90-entry default) local history of PR attention counts and query-error totals. The scheduled workflow currently uploads a **single-run history entry** alongside its snapshot; GitHub Actions workspaces are ephemeral, so this is not cross-run persistence. Retain previous artifacts locally and supply the same history file to append across days. No workflow writes to the repository or external storage.\n\n**Latest integration gate:** see [the exact-head readiness matrix](ENGINEERING_WORK_QUEUE.md#exact-head-integration-readiness-audit--2026-10-24) for per-repository CI observations, base drift and action owners. It supersedes older mergeability notes; none of the observations authorizes a merge.\n\nThis is a **dated planning snapshot**, not live CI or release certification. Use the [refresh script](../scripts/portfolio_status.py) to retrieve current public GitHub state. The snapshot was assembled 2026-10-24 UTC. Never turn a passed source CI check into a claim of released functionality.

| Project | Engineering goal | Known review/release gate | Foundation PR |
| --- | --- | --- | --- |
| [Grid Atlas](https://github.com/vlovers/grid-atlas) | Source-backed UK/EN archive | Editorial/media approvals, real-archive acceptance, beta operations #104 | [#268](https://github.com/vlovers/grid-atlas/pull/268) |
| [AI Office](https://github.com/vlovers/ai-office) | Safe local agent workflow | Real Codex/sandbox and release stabilization | [#43](https://github.com/vlovers/ai-office/pull/43) |
| [RuleWitness](https://github.com/vlovers/rulewitness) | Conservative configured-policy analysis | v0.4 release readiness, uncertainty and installed consumer verification | [#82](https://github.com/vlovers/rulewitness/pull/82) |
| [MutationBoundary](https://github.com/vlovers/mutation-boundary) | Disposable PostgreSQL net-state assertions | Package/consumer and safety regression | [#68](https://github.com/vlovers/mutation-boundary/pull/68) |
| [Estima](https://github.com/vlovers/estima) | Multi-tenant time estimation | Clarification atomicity #10, migrations, tenant security | [#13](https://github.com/vlovers/estima/pull/13) |
| [Last Chapter](https://github.com/vlovers/last-chapter) | Reproducible, agent-friendly narrative-game engineering foundation | [#1](https://github.com/vlovers/last-chapter/issues/1) lockfile, `npm ci`, format/lint/typecheck/tests/build; draft PR not merge-ready | [#5](https://github.com/vlovers/last-chapter/pull/5) |

**Excluded by request:** Frostline. The separate RuleWitness consumer-E2E repository is treated as a verification fixture, not another product.

**Workstream ownership:** the portfolio coordinator handles repository governance, review/CI evidence, issue triage and agent handoffs only. Product content, UI, narrative, gameplay and feature defects are assigned to the relevant product delivery workstream; they are not implemented or independently filed by governance without an explicit request. See [operational ownership and Last Chapter acceptance](ENGINEERING_ROLLOUT_AUDIT.md#operational-ownership-and-last-chapter-onboarding--2026-10-24).

## Issue triage — prioritized

| Priority | Repository | Existing issue/PR | Required action before closing |
| --- | --- | --- | --- |
| P0 | Estima | [issue #10](https://github.com/vlovers/estima/issues/10), [PR #11](https://github.com/vlovers/estima/pull/11) | Verify atomic persistence, concurrent retry safety, real PostgreSQL integration evidence; do not close from existence of tests alone |
| P0 | RuleWitness | [issue #79](https://github.com/vlovers/rulewitness/issues/79), [PR #81](https://github.com/vlovers/rulewitness/pull/81) | Verify actual registry version, immutable tarball, publish/consumer evidence and security gates; no automatic publishing |
| P0 | Grid Atlas | [issue #104](https://github.com/vlovers/grid-atlas/issues/104) | Confirm release protections, deployment, backup/restore, secrets, TLS, real-origin smoke |
| P1 | Grid Atlas | [issues #106, #134, #155, #199](https://github.com/vlovers/grid-atlas/issues) | Compare merged PRs with **each original acceptance criterion**; close only after actual UX/source/CI verification |
| P1 | Grid Atlas | [issues #107, #133, #145, #152, #161, #195](https://github.com/vlovers/grid-atlas/issues) | Separate implemented UI from pending human editorial/media/design acceptance; retain incomplete goals |
| P2 | Grid Atlas | [issue #123](https://github.com/vlovers/grid-atlas/issues/123) | Inspect remaining untranslated inline strings before closure |
| P1 | AI Office | [PR #41](https://github.com/vlovers/ai-office/pull/41) | Review safe read-only GitHub preflight and compatibility with existing agent permissions |
| Maintenance | MutationBoundary | [issues](https://github.com/vlovers/mutation-boundary/issues) | No open issues in audit; continue regression and consumer monitoring |

## Definition of dashboard fields

- **Code status:** implementation PR exists/merged; not a feature acceptance signal.
- **Verification:** exact commit SHA plus observed Actions job conclusions; unknown must remain unknown.
- **Product acceptance:** maintained separately by original user-visible acceptance criteria, human editorial/security review where needed.
- **Release:** immutable tag/registry publication or verified deployment, not package.json version or README alone.
- **Blocked by:** unresolved safety, data integrity, security, licensing, release evidence or user acceptance gates.

## Refresh and review

```sh
python3 scripts/portfolio_status.py
# Optional authentication for larger API quotas:
GITHUB_TOKEN=... python3 scripts/portfolio_status.py
```

The script performs read-only GitHub API requests and prints current default-branch commit SHA, open PR/issue counts and latest GitHub release tag **where available**. It also checks **seven foundation PRs** (including this portfolio PR and merged Grid Atlas #268) and **nine existing issue-intake / CI-security PRs**, reports each **current PR head SHA** and GitHub's transient mergeability observation (never merge authorization), summarizes **observed pull-request GitHub Actions runs only for that exact SHA**, and fetches **all PR review pages** to distinguish current-head non-author approvals from historical/dismissed reviews and outstanding change requests. It reuses each tracked PR's metadata within a single report execution (avoiding up to 14 duplicate PR requests) but does not cache metadata across runs. It additionally compares **all tracked, unmerged engineering PRs** against their named live target branches (`main` or `develop`) to show base-only and PR-only commit counts; it does **not** treat `base.sha` from PR metadata as the current branch tip or equate divergence with merge conflicts. An approval observation is not proof of reviewer independence or maintainer acceptance. It does not certify required checks, branch rules, user-facing feature completeness, merge authorization, or release readiness. It never mutates GitHub objects, closes issues, merges PRs, or publishes packages.

**Untrusted GitHub metadata:** the report validates 40-character commit SHAs, default-branch names and release-tag cell content before rendering. Release metadata cannot inject Markdown rows or control characters; malformed data produces an unknown repository row and a nonzero exit code. Review evidence requires an explicit GitHub account type: bot, organization and mannequin accounts cannot be counted as independent non-author approvals, and missing/unknown account types fail closed. Actions pagination counts must be actual integers, not boolean JSON values. Offline regression tests exercise these boundaries; this is report integrity hardening, not GitHub ruleset enforcement.

**Fail-closed semantics:** missing or mismatched Actions runs, incomplete pagination, malformed Actions run metadata, skipped/neutral checks, malformed PR or reviewer metadata, stale/dismissed approvals, and API failures never become a green result. A failed lookup for any of the 15 tracked PRs produces an unknown row and a nonzero exit status. A failed tracked PR live-base comparison likewise produces unknown and a nonzero exit status. A failed workflow is reported as a failure; a pending workflow is not considered passed. A successful observed run does not prove that all required checks exist or that independent acceptance occurred. The script returns a nonzero exit code if any repository, foundation-PR, or review query fails. Review submissions are chronological observations; repository rulesets, CODEOWNERS and reviewer independence must still be checked separately. Use an authorized read-only `GITHUB_TOKEN` for repeat runs to avoid unauthenticated rate limits; never put tokens in generated Markdown or CI logs.

**CI scope:** `portfolio-validation.yml` runs offline regression tests and Python compilation on script, test, workflow **and dashboard documentation** changes. It does not query live GitHub or verify branch-protection settings; use the report manually for live status.

At each iteration: read fresh status, revisit issue criteria, choose one cohesive feature outcome per active project, and retain dated decisions or blockers. Do not manually edit counts without verifying them.

### Mergeability evidence policy

GitHub's `mergeable` value is a point-in-time computation and may flip as its mergeability calculation completes. When it is `false`, repeat the query and inspect the reverse `PR head...base` comparison, changed-file overlap, and the exact-head Actions results before labeling the issue a persistent conflict. A successful CI run on a PR head does not certify the final merge commit, and `mergeable=true` does not replace independent review or branch rules.

### Daily history persistence

The scheduled workflow restores the most recent unexpired `engineering-portfolio-snapshot` artifact using the read-only Actions API, appends the current run to `portfolio-history.json`, and uploads it again. This is **artifact-backed rolling history**, not permanent storage: artifacts expire after 14 days, and a gap longer than retention starts a fresh history. The first run also starts fresh. Restoration failures fail the history step rather than silently pretending continuity. No GitHub write token or repository commits are required. Verify behavior with a manual `workflow_dispatch` run after the workflow reaches the default branch.

Artifact restoration checks up to five pages of recent Actions artifacts, excludes the current run and expired artifacts, and validates chronological order before reuse. If the repository produces more than 500 artifacts in the retention window, the search is bounded and may not find the oldest history; a longer-term archive would need separate storage and explicit approval.

### Audited overlap evidence freshness

Known changed-file overlaps are explicitly pinned to the full 40-character PR head SHAs observed during the audit. The Markdown renderer marks an overlap audit **stale** if either PR head changes, **unknown** if its SHA is unavailable, and **re-audit against new base** if either PR was merged. This is not live overlap discovery and must never be interpreted as conflict clearance. Recompute changed-file lists and update audited SHAs after every head change.
