# Engineering work queue

Updated 2026-10-24. This is a **coordination backlog**, not product implementation or authorization to merge. Review links are the source of truth; CI evidence is exact-commit only.

## P0 — Integration readiness

| Owner lane | PRs / dependency order | Next independently executable engineering action | Gate |
| --- | --- | --- | --- |
| Portfolio | [#2](https://github.com/vlovers/vlovers/pull/2) | Keep repository inventory, branch-drift report and offline tests aligned; review CI on final SHA | Human acceptance; no auto-merge |
| AI Office | [#43](https://github.com/vlovers/ai-office/pull/43) → [#48](https://github.com/vlovers/ai-office/pull/48) → [#49](https://github.com/vlovers/ai-office/pull/49) | Check overlapping docs and package scripts; re-run CI after base changes | Preserve security tests and no product changes |
| RuleWitness | [#82](https://github.com/vlovers/rulewitness/pull/82) → [#83](https://github.com/vlovers/rulewitness/pull/83) | Verify issue-intake security disclosure and test agreement | No fabricated approvals |
| MutationBoundary | [#68](https://github.com/vlovers/mutation-boundary/pull/68) → [#69](https://github.com/vlovers/mutation-boundary/pull/69) → [#70](https://github.com/vlovers/mutation-boundary/pull/70) | Resolve `CONTRIBUTING.md` overlap and retain **v0.6.0** release history when applying provenance gate | No release/tag/publish |
| Estima | [#13](https://github.com/vlovers/estima/pull/13) → [#14](https://github.com/vlovers/estima/pull/14) → [#15](https://github.com/vlovers/estima/pull/15) | Review on target **develop**, preserve real PostgreSQL CI | No switch to main |
| Grid Atlas | [#271](https://github.com/vlovers/grid-atlas/pull/271) → [#272](https://github.com/vlovers/grid-atlas/pull/272) | Verify pinned workflows; wait for product owner to resolve browser CI failure | Never weaken accessibility test |
| Last Chapter | [draft #5](https://github.com/vlovers/last-chapter/pull/5) / [issue #1](https://github.com/vlovers/last-chapter/issues/1) | Verify committed lockfile, `npm ci`, and final-head CI; author decides draft readiness | Product code belongs to game team |

## Live verification — 2026-10-24 (exact PR head observations)

These are observations, **not** merge authorization. Re-check after every push.

| PR | Head SHA prefix | Observed Actions runs | GitHub mergeability | Engineering follow-up |
| --- | --- | --- | --- | --- |
| [Grid Atlas #271](https://github.com/vlovers/grid-atlas/pull/271) | `6c93c1c87` | 1 success | false | Resolve branch conflict without changing product code |
| [Grid Atlas #272](https://github.com/vlovers/grid-atlas/pull/272) | `1c22563d0` | 8 success, 1 failure, 1 cancelled | false | Identify failing check and resolve integration conflict; do not disable browser checks |
| [Last Chapter #5](https://github.com/vlovers/last-chapter/pull/5) | `d9d79b088` | 1 failure | true | Inspect current failed job; earlier green SHA is superseded |

Other observed PR mergeability (not approval): AI Office #43/#48/#49, RuleWitness #82/#83, MutationBoundary #68/#69/#70 and Estima #13/#14/#15 were reported mergeable by GitHub. Their current exact-head CI has **not** been re-certified in this verification batch.

## P1 — Dashboard engineering

1. Keep six-repository inventory and 16 tracked PRs accurate (seven foundation, nine follow-up); reconcile closed or superseded PRs without silently removing history.
2. Provide **read-only**, exact-head CI, review and branch-drift evidence. Missing API data must render **unknown**, never green.
3. Add a machine-readable snapshot export with stable schema, offline tests and bounded pagination; do not publish tokens or sensitive API data.
4. Add stale-PR age, blocker ownership and dependency status **only when backed by GitHub timestamps/explicit metadata**, not guesses.
5. Add scheduled report generation only after selecting safe GitHub token permissions, update frequency and destination. Do not automatically write Issues or merge PRs.

## P1 — Agent coordination

- Each task requires owner, repository, base branch, scoped files, acceptance criteria, checks, dependencies and explicit non-goals.
- One active owner per overlapping file set. Changes in product code are routed to product workstreams.
- Before handoff, attach PR URL, exact head SHA, check conclusions, changed paths and remaining blockers.
- No agent may independently merge, release, delete, force-push, modify secrets or weaken checks.

## Deferred owner actions

- [Branch ruleset setup](BRANCH_RULESET_SETUP.md): GitHub Administration access and owner confirmation required.
- Independent review availability and CODEOWNERS policy: owner decision required before enforcing approval count.
- All product feature, narrative, UI and gameplay implementation is **out of scope** for engineering coordination.

## Definition of completion

A work item is ready for review only when the scoped change exists in a PR, checks are observed on its **current SHA**, conflicts and dependency blockers are documented, and any human decision is explicitly pending or recorded. `mergeable=true` alone is never approval.
