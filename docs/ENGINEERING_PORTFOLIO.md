# Engineering portfolio — active projects

**Engineering normalization:** see the [verified rollout audit, gap matrix and cleanup gates](ENGINEERING_ROLLOUT_AUDIT.md).

This is a **dated planning snapshot**, not live CI or release certification. Use the [refresh script](../scripts/portfolio_status.py) to retrieve current public GitHub state. The snapshot was assembled 2026-10-24 UTC. Never turn a passed source CI check into a claim of released functionality.

| Project | Engineering goal | Known review/release gate | Foundation PR |
| --- | --- | --- | --- |
| [Grid Atlas](https://github.com/vlovers/grid-atlas) | Source-backed UK/EN archive | Editorial/media approvals, real-archive acceptance, beta operations #104 | [#268](https://github.com/vlovers/grid-atlas/pull/268) |
| [AI Office](https://github.com/vlovers/ai-office) | Safe local agent workflow | Real Codex/sandbox and release stabilization | [#43](https://github.com/vlovers/ai-office/pull/43) |
| [RuleWitness](https://github.com/vlovers/rulewitness) | Conservative configured-policy analysis | v0.4 release readiness, uncertainty and installed consumer verification | [#82](https://github.com/vlovers/rulewitness/pull/82) |
| [MutationBoundary](https://github.com/vlovers/mutation-boundary) | Disposable PostgreSQL net-state assertions | Package/consumer and safety regression | [#68](https://github.com/vlovers/mutation-boundary/pull/68) |
| [Estima](https://github.com/vlovers/estima) | Multi-tenant time estimation | Clarification atomicity #10, migrations, tenant security | [#13](https://github.com/vlovers/estima/pull/13) |

**Excluded by request:** Frostline. The separate RuleWitness consumer-E2E repository is treated as a verification fixture, not a sixth product.

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

The script performs read-only GitHub API requests and prints current default-branch commit SHA, open PR/issue counts and latest GitHub release tag **where available**. It also checks the six tracked engineering foundation PRs (including this portfolio PR and merged Grid Atlas #268), reports their **current PR head SHA**, and summarizes **observed pull-request GitHub Actions runs only for that exact SHA**. It does not certify required checks, reviewer approval, branch rules, user-facing feature completeness, or release readiness. It never mutates GitHub objects, closes issues, merges PRs, or publishes packages.

**Fail-closed semantics:** missing or mismatched Actions runs, incomplete pagination, skipped/neutral checks, malformed PR metadata, and API failures never become a green result. A failed workflow is reported as a failure; a pending workflow is not considered passed. A successful observed run does not prove that all required checks exist or that independent acceptance occurred. The script returns a nonzero exit code if any repository or foundation-PR query fails. Use an authorized read-only `GITHUB_TOKEN` for repeat runs to avoid unauthenticated rate limits; never put tokens in generated Markdown or CI logs.

**CI scope:** `portfolio-validation.yml` runs offline regression tests and Python compilation on script, test, workflow **and dashboard documentation** changes. It does not query live GitHub or verify branch-protection settings; use the report manually for live status.

At each iteration: read fresh status, revisit issue criteria, choose one cohesive feature outcome per active project, and retain dated decisions or blockers. Do not manually edit counts without verifying them.
