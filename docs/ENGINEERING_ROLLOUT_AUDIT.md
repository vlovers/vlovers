# Engineering rollout audit — 2026-10-24

Scope: **grid-atlas, ai-office, rulewitness, mutation-boundary, estima** and portfolio/profile repository. Frostline excluded by owner request.

This is a **verified presence/queue audit**, not a claim that code quality, external dependencies, secrets, build matrices or all issues have been completely reviewed. Do not close items from this report alone.

## Observed repository inventory

| Repository | AGENTS on default branch | CONTRIBUTING | SECURITY | Dependabot | Foundation PR | Open product PRs / issues at audit |
| --- | --- | --- | --- | --- | --- | --- |
| grid-atlas | yes | yes | yes | no | #268 merged | #267; 12 issues |
| ai-office | no | yes | yes | yes | #43 open | #46, #47; 0 issues |
| rulewitness | no | yes | yes | yes | #82 open | #81; 2 issues |
| mutation-boundary | no | yes | yes | no | #68 open | none; 0 issues |
| estima | no | no | no | no | #13 open | #11; issue #10 |

Presence alone does not prove policy quality. Existing project-specific commands, fixtures and security constraints remain authoritative until individually reviewed.

## Acceptance requirements for a consistent baseline

1. **Repository discovery:** accurate README / ownership / current branch, supported environments and limitations.
2. **Agent contracts:** AGENTS.md canonical, CLAUDE.md delegates, minimal context and project-specific safety boundaries. Paths and scripts must exist.
3. **Contributor workflow:** CONTRIBUTING.md, triage labels and issue templates, PR template with acceptance criteria, evidence and N/A justifications.
4. **Safety:** private vulnerability reporting or safe contact, no secrets/test credentials, branch protection, least-privilege GitHub Actions tokens; dependency update policy appropriate to lockfile manager.
5. **Verification:** reproducible install, formatting, lint/typecheck, unit, integration, E2E with disposable fixtures, security/contract tests, documented environment gaps; required status checks configured in branch rules.
6. **Review:** human accountable owner; second-context reviewer for meaningful changes, independent validation for security and data migrations; no self-attested approval. Copilot Pro is **not required**.
7. **Release:** changelog/version/tag/registry or deployment evidence, smoke, rollback, rollback owner, no automatic publish on docs-only PR.
8. **Portfolio:** one authoritative issue queue per repo, central read-only status projection, link to acceptance evidence; never infer green/ready from counts.

## Cleanup policy

Before closing or deleting anything: inspect last code changes, linked PRs, acceptance criteria and consumers. Classify each candidate **KEEP / MERGE INTO CANONICAL / ARCHIVE / CLOSE AS VERIFIED / BLOCKED** with proof and redirect links. Avoid deleting historical evidence and avoid closing broad product epics merely because features exist in code. No mass close/merge.

## Ordered work packages

### P0: Foundation PR integration

- [ ] MutationBoundary [#68](https://github.com/vlovers/mutation-boundary/pull/68) — independent audit then merge on exact SHA.
- [ ] RuleWitness [#82](https://github.com/vlovers/rulewitness/pull/82) — independent audit and verify permission/posture guarantees.
- [ ] AI Office [#43](https://github.com/vlovers/ai-office/pull/43) — reconcile with current main and verify permission-boundary docs.
- [x] Grid Atlas [#268](https://github.com/vlovers/grid-atlas/pull/268) — merged; six canonical files verified on main.
- [ ] Estima [#13](https://github.com/vlovers/estima/pull/13) — review develop-target, existing scripts and migration rules.
- [ ] Portfolio [#2](https://github.com/vlovers/vlovers/pull/2) — verify read-only report CI and merge.

### P1: Gap remediation (separate cohesive PR per repo)

- [ ] Estima: add concise CONTRIBUTING, SECURITY, issue templates, dependency strategy, CI gate/branch-rule audit. Do **not** change database behavior in this work package.
- [ ] Grid Atlas and MutationBoundary: assess existing dependency strategy before adding Dependabot, including noise, safe automerge policy (default: off), ecosystem compatibility.
- [ ] AI Office / RuleWitness: validate Dependabot schedules and GitHub Actions permissions; check all paths/scripts inside agent guides.
- [ ] All five: audit current workflows and branch protections against documented DoD; classify tests as smoke/mock/real and document coverage gaps.

### P2: Issues and work tracking

- [ ] Grid Atlas: triage 12 open issues against exact acceptance criteria; explicitly distinguish implementation from editorial/design/release acceptance.
- [ ] RuleWitness: #79 release evidence and #69 independent consumer semantics.
- [ ] Estima: #10 atomic clarification and PR #11 experiment; verify DB tests before closure.
- [ ] AI Office: existing #46/#47 feature PRs need acceptance evidence, and visible issue tracking for new work.
- [ ] MutationBoundary: maintain issues for verified bugs; avoid placeholder backlog.
- [ ] Portfolio: current profile repository has Issues disabled (GitHub returned HTTP 410). Prefer central GitHub Project if available, or maintain this document as a non-duplicating index. Do not claim central Issues are active.

### P3: Operational workflow

- [ ] Configure enforceable branch rules/required checks via repository settings and record what GitHub actually enforces.
- [ ] Run one *documentation-only* test PR per repo to verify PR template, required CI and review process; do not claim review automation unless it executes.
- [ ] Merge/accept/release only after defined gates, and record actual SHA and evidence.
- [ ] Schedule read-only dashboard refresh only with an authorized trigger and appropriate access controls.

## Scope boundary

**No new product features until P0 and critical P1 workflow foundations are accepted.** Risky data/security issues can still be addressed as incident fixes, separately from feature work.

## Foundation PR exact-head verification — 2026-10-24

The six baseline PRs were checked against their **current head SHA**, not a previous commit. This is observed PR Actions evidence only; it is **not** independent review, branch-rule enforcement, acceptance or merge authorization.

| Foundation PR | Head SHA | Observed Actions |
| --- | --- | --- |
| [Grid Atlas #268](https://github.com/vlovers/grid-atlas/pull/268) | `c03c68f96a87` | Merged; Foundation CI success on former PR head |
| [AI Office #43](https://github.com/vlovers/ai-office/pull/43) | `3eb4eaae2b8c` | [AI Office validation #40105333564](https://github.com/vlovers/ai-office/actions/runs/40105333564) success |
| [RuleWitness #82](https://github.com/vlovers/rulewitness/pull/82) | `7ea6357de953` | CI + permissions review success |
| [MutationBoundary #68](https://github.com/vlovers/mutation-boundary/pull/68) | `d901cc88697a` | [MutationBoundary checks #40105239826](https://github.com/vlovers/mutation-boundary/actions/runs/40105239826) success |
| [Estima #13](https://github.com/vlovers/estima/pull/13) | `804873ea0b0c` | Bun + PostgreSQL integration success |
| [Portfolio #2](https://github.com/vlovers/vlovers/pull/2) | `b0618462e500` (before this audit edit) | [Portfolio report validation #40121960041](https://github.com/vlovers/vlovers/actions/runs/40121960041) success; **rerun required after this documentation commit** |

All five still-open baseline PRs require independent review and maintainer acceptance. A historical success does not apply after a new push.

## Independent-review gate — observed 2026-10-24

The five open foundation PRs [MutationBoundary #68](https://github.com/vlovers/mutation-boundary/pull/68), [RuleWitness #82](https://github.com/vlovers/rulewitness/pull/82), [Estima #13](https://github.com/vlovers/estima/pull/13), [AI Office #43](https://github.com/vlovers/ai-office/pull/43) and [Portfolio #2](https://github.com/vlovers/vlovers/pull/2) have successful observed PR Actions on the SHAs checked. **No independent approval was confirmed**: the first four have only author-account COMMENTED technical assessments in the reviewed submissions, and Portfolio #2 had no review submissions. The AI Office review comments also flag possible branch divergence; current GitHub PR metadata reports `mergeable=true`, but that alone cannot resolve the reviewer-requested branch integration and sandbox acceptance. A fresh review of the final diff, branch rules and latest CI SHA is still required. Do not merge based on this audit.

The portfolio report now exposes read-only review observations separately from Actions evidence. It rejects incomplete review pagination, ignores author and bot approvals, treats historical/dismissed approvals as insufficient, and reports outstanding change requests. **Even a current-head approval from another account is not certification of independence or branch-rule compliance.** Do not infer maintainer acceptance or merge authorization from this table or script.

## Intake and CI hardening queue — verified 2026-10-24

These are **separate open PRs**, not deployed default-branch changes. CI observations were rechecked 2026-10-24; refresh before relying on them. Keep acceptance and release states distinct.

| Repository | Intake / contributor PR | CI supply-chain PR | Last observed CI state |
| --- | --- | --- | --- |
| Grid Atlas | [#271](https://github.com/vlovers/grid-atlas/pull/271) | [#272](https://github.com/vlovers/grid-atlas/pull/272) | #271 Foundation CI passed. **#272 currently has 8 successful, 1 failed, 1 cancelled workflow** on head `1c22563d0ec0` (Unified archive experience failed; Next.js web cancelled). The earlier 9/9 observation was for a different/historical SHA and must not be treated as current-head evidence. |
| AI Office | [#48](https://github.com/vlovers/ai-office/pull/48) | [#49](https://github.com/vlovers/ai-office/pull/49) | Both validation runs passed on respective head SHAs |
| RuleWitness | [#83](https://github.com/vlovers/rulewitness/pull/83) | Existing pinned and read-only CI | CI + permissions review passed on #83 head |
| MutationBoundary | [#69](https://github.com/vlovers/mutation-boundary/pull/69) | [#70](https://github.com/vlovers/mutation-boundary/pull/70) | #69 and #70 checks passed on respective head SHAs; #70 release guard not deployed |
| Estima | [#14](https://github.com/vlovers/estima/pull/14) | [#15](https://github.com/vlovers/estima/pull/15) | PostgreSQL + Bun workflows passed on both heads; CI hardening not merged |

**Integration rule:** before opening another broad standardization PR, finish the existing queue or document a verified blocker. The PR author cannot self-certify independence simply by running another prompt. Confirm real repository rulesets and approvals through GitHub settings or an authorized reviewer; current GitHub connector does not expose branch protection settings. AI Office branch divergence was independently rechecked on 2026-10-24 using `compare(head...main)`: #43 was **15 commits behind** `main` (13 ahead), #48 **12 behind** (9 ahead), and #49 **12 behind** (11 ahead). The upstream-only changes include delivery publication and Git-transfer code/docs. All three PRs were open and reported mergeable when checked; mergeability does **not** establish that their documentation reflects the current delivery security boundary. Before independent acceptance, compare the final base-to-head diff against current `main`, inspect overlap with `ROADMAP.md` and delivery security docs, and reconcile only after deciding whether rebase/merge is safe for the existing review history. Record a fresh SHA and rerun CI after any branch update. Do not automatically merge `main` into the PR branches or claim prior CI applies to a rewritten head.

**Review focus:** malformed GitHub Issue YAML front matter, reporter security guidance, duplicate template options, unpinned third-party actions, persistent checkout credentials and CI on the exact final head. Resolve with narrow commits to the current PR branches; do not mass-close Issues or auto-merge.

## Read-only follow-up PR verification — 2026-10-24

Rechecked **all nine existing intake/CI-security PRs** at their current head SHA. This is a dated Actions observation, not an approval or claim that security controls have been deployed to the default branch.

| Repo / PR | Head SHA | Observed PR Actions | Integration note |
| --- | --- | --- | --- |
| [Grid Atlas #271](https://github.com/vlovers/grid-atlas/pull/271) | `6c93c1c87219` | Foundation CI 1/1 success | open |
| [Grid Atlas #272](https://github.com/vlovers/grid-atlas/pull/272) | `4aeab9b78c81` | 9/9 success | open; independent review pending |
| [AI Office #48](https://github.com/vlovers/ai-office/pull/48) | `298cd4682b5e` | validation 1/1 success | open; branch diverged from latest main |
| [AI Office #49](https://github.com/vlovers/ai-office/pull/49) | `31e4b3e4ead7` | validation 1/1 success | open; branch diverged from latest main |
| [RuleWitness #83](https://github.com/vlovers/rulewitness/pull/83) | `9cd3713a7b41` | CI + permissions review 2/2 success | open |
| [MutationBoundary #69](https://github.com/vlovers/mutation-boundary/pull/69) | `8b830e3fe622` | checks 1/1 success | open |
| [MutationBoundary #70](https://github.com/vlovers/mutation-boundary/pull/70) | `4e67f8b95c53` | checks 1/1 success | open; release guard not deployed |
| [Estima #14](https://github.com/vlovers/estima/pull/14) | `1b8b9e8e9233` | Bun + PostgreSQL 2/2 success | open; target develop |
| [Estima #15](https://github.com/vlovers/estima/pull/15) | `4116230468e2` | Bun + PostgreSQL 2/2 success | open; target develop |

**AI Office branch integration:** reverse comparison from foundation #43 to latest `main` shows **14 commits on main absent from that branch** as of this audit; #48 and #49 each show **11**. GitHub reports the PRs mergeable on the latest read, but this does not substitute for integrating current main and re-running validation on the resulting SHA. Do not automatically rebase, force-push, or merge to satisfy a dashboard indicator.

The [portfolio refresh script](../scripts/portfolio_status.py) now observes both the six foundation PRs and these nine follow-ups with exact-head CI and non-author review evidence. Unknown/malformed API responses are never accepted as green. Its offline CI tests do not query live GitHub, and it does not inspect repository branch protection or required-check rules.



## AI Office live-base reconciliation checkpoint — 2026-10-24

Fresh comparisons against the **named live `main` ref** (not the historical `base.sha` from PR metadata) show the following integration backlog. These counts are Git history divergence, **not merge conflicts**; they change as `main` advances.

| PR | PR head | Live `main`-only commits | PR-only commits | Integration status |
| --- | --- | ---: | ---: | --- |
| [#43](https://github.com/vlovers/ai-office/pull/43) | `87d7f8c1f01d` | 16 | 13 | Open; independent review and reconciliation outstanding |
| [#48](https://github.com/vlovers/ai-office/pull/48) | `298cd4682b5e` | 13 | 9 | Open; independent review and reconciliation outstanding |
| [#49](https://github.com/vlovers/ai-office/pull/49) | `31e4b3e4ead7` | 13 | 11 | Open; independent review and reconciliation outstanding |

**Important API trap:** comparing `PR base.sha...PR head.sha` showed zero base-only commits because the observed `base.sha` values represented the original shared ancestor, **not the current tip of `main`**. The portfolio script now compares `PR head SHA...live base ref` for these three PRs, validates response metadata, and fails closed on compare errors. The report is read-only and cannot prove GitHub ruleset compliance or authorize a merge.

**Next acceptance batch:** independently inspect all three PRs against current `main`, including delivery publication/Git-transfer documentation and workflow security interactions; decide integration order and reconcile in existing branches only after review. Re-run CI on each new head and record base/head SHA and reviewer disposition. Do not assume the existing successful PR checks validate the future integrated result.

## Cross-repository exact-head CI checkpoint — 2026-10-24

Rechecked all **13 open normalization PRs** across the five product repositories. All observed PR-triggered workflows completed successfully on the exact heads listed below. This is a dated observation, **not** independent review, a required-check/ruleset audit, or permission to merge. GitHub's `mergeable` field can be transient; in particular, AI Office #49 returned `false` during this check and requires a fresh integration/conflict inspection.

| Repository | PRs and exact-head observed CI |
| --- | --- |
| Grid Atlas | [#271](https://github.com/vlovers/grid-atlas/pull/271) `6c93c1c87219` — 1/1; [#272](https://github.com/vlovers/grid-atlas/pull/272) `17b5f56ff0a` — 9/9 |
| AI Office | [#43](https://github.com/vlovers/ai-office/pull/43) `3eb4eaae2b8c` — 1/1; [#48](https://github.com/vlovers/ai-office/pull/48) `345706befe81` — 1/1; [#49](https://github.com/vlovers/ai-office/pull/49) `c42437335341` — 1/1 (mergeability needs recheck) |
| RuleWitness | [#82](https://github.com/vlovers/rulewitness/pull/82) `7ea6357de953` — 2/2; [#83](https://github.com/vlovers/rulewitness/pull/83) `f01938a7c96a` — 2/2 |
| MutationBoundary | [#68](https://github.com/vlovers/mutation-boundary/pull/68) `d901cc88697a` — 1/1; [#69](https://github.com/vlovers/mutation-boundary/pull/69) `8b830e3fe622` — 1/1; [#70](https://github.com/vlovers/mutation-boundary/pull/70) `4e67f8b95c53` — 1/1 |
| Estima (target: develop) | [#13](https://github.com/vlovers/estima/pull/13) `804873ea0b0c` — 2/2; [#14](https://github.com/vlovers/estima/pull/14) `1b8b9e8e9233` — 2/2; [#15](https://github.com/vlovers/estima/pull/15) `02476a143dc2` — 2/2 |

**Integration queue:** obtain non-author review and inspect the final diff/target-branch divergence before merging. Prioritize AI Office #49 mergeability diagnosis, then reconcile any stale PR bases without force-pushing away review evidence. Re-run exact-head CI after integration commits. Do not close product issues from workflow success alone.


## AI Office #49 integration diagnosis — 2026-10-24

[CI security PR #49](https://github.com/vlovers/ai-office/pull/49) is **green on head `c42437335341` (1/1 Actions)**, but repeated GitHub metadata reads report `mergeable=false`. A fresh `compare(head...main)` reports **17 main-only and 15 PR-only commits**. This is evidence of divergence, not itself a proof of textual conflicts.

The PR patch changes only four files: `.github/workflows/validation.yml`, `package.json`, `scripts/check-workflow-action-pins.mjs`, and `tests/workflow-action-pins.test.mjs`. The upstream comparison includes `.github/workflows/validation.yml` and `package.json` among changed paths, so these are the first files to inspect for overlap. The comparison also includes extensive product-specific delivery code; **do not import or rewrite that product code as part of engineering standardization**.

**Next safe action:** review the current main versions of the two overlapping files and resolve any actual conflicts in the existing #49 branch, preserving immutable action SHAs, `persist-credentials: false`, and the current main validation jobs. Then rerun CI on the resulting head and obtain independent review. Do not force-push, auto-merge, or infer that a passing pre-integration workflow certifies the future merged result.



## Integration checkpoint after conflict resolution — 2026-10-24

This checkpoint supersedes **earlier dated mergeability observations** above; the historical SHA tables remain for audit traceability, not current status. Read-only GitHub PR metadata and exact-head Actions runs were checked again.

| Repository / PR | Verified head | Exact-head Actions | GitHub mergeability |
| --- | --- | --- | --- |
| [AI Office #49](https://github.com/vlovers/ai-office/pull/49) | `36f01c4bd879` | 1/1 completed success | `true` |
| [Grid Atlas #271](https://github.com/vlovers/grid-atlas/pull/271) | `6c93c1c87219` | 1/1 completed success | `true` |
| [Grid Atlas #272](https://github.com/vlovers/grid-atlas/pull/272) | `17b5f56ff0a` | 9/9 completed success | `true` |

AI Office #49 previously had a **confirmed `package.json` textual conflict** against `main` (GitHub conflict editor), not merely commit divergence. The conflict was resolved in its PR branch, and the resulting head was inspected for the full `check` chain (workflow pin checks, workflow tests, security lint, typecheck, tests, smoke, build), matching `package-lock.json` dev dependencies, security lint in CI, and immutable Actions checks. The subsequent exact-head Actions run completed successfully. This does **not** establish independent review or authorize merging.

The remaining infrastructure queue was rechecked for GitHub mergeability: AI Office #43/#48, RuleWitness #82/#83, MutationBoundary #68/#69/#70, and Estima #13/#14/#15 all returned `true` while still open. A transient `mergeable=true` observation is not a repository ruleset or reviewer approval check. No merges or product-code edits were performed.

The [central portfolio PR #2](https://github.com/vlovers/vlovers/pull/2) additionally has an exact-head successful offline test run on `6a7982b6e888`; the report now reuses PR metadata per execution and exposes transient GitHub mergeability. The test suite was updated after a failed run caused by old fixtures expecting four fields rather than five. Later commits require their own CI evidence.

**Next review gate:** verify current head and required checks immediately before integration, obtain an authorized independent review, and validate each repository's branch rules. Avoid inferring release readiness or product acceptance from these CI observations.


## Integration order and review gate — 2026-10-24

Fresh GraphQL review-submission inspection of all **14 open engineering PRs** (13 product-repository PRs plus portfolio #2) found **zero `APPROVED` submissions**. AI Office #43, RuleWitness #82, MutationBoundary #68, and Estima #13 have owner `COMMENTED` review entries; comments are not approvals or independent review. This is an observation of the available review history, not a branch-ruleset audit.

**Recommended integration sequence, subject to authorized review and fresh exact-head CI:**

| Repository | Review / integration order | Why |
| --- | --- | --- |
| Grid Atlas | #271 issue templates → #272 CI security | Separate template scope from broad CI changes; #272 also includes `apps/web/src/components/atlas/catalogue.module.css`, so inspect this unexpected product-style diff and do not treat it as CI-only |
| AI Office | #43 agent foundation → #48 issue intake → #49 CI security | Distinct file sets in the current PR patches; #49 has already integrated latest `main` to resolve its `package.json` conflict; preserve lint and workflow pin checks |
| RuleWitness | #82 agent foundation → #83 issue intake | #83 changes `SECURITY.md` and adds tests; verify security reporting instructions and test behavior |
| MutationBoundary | #68 foundation → #69 intake → #70 CI/release guard | #68/#69 both modify `CONTRIBUTING.md`; #68/#70 both modify `README.md` and `docs/RELEASING.md`. Recheck these shared files after each integration. #70 changes publish workflow: verify release safety, never trigger publication as part of normalization |
| Estima | #13 foundation → #14 intake → #15 CI security (target `develop`) | #14 changes `SECURITY.md`; #15 changes Bun/PostgreSQL workflows. Preserve real database validation; do not redirect to `main` |
| Central dashboard | #2 after reviewer acceptance | Read-only report and offline tests; do not mistake mergeability or observed CI for ruleset compliance |

**Before each merge:** inspect the current base-to-head diff and unexpected paths; obtain the appropriate reviewer decision; verify branch protection/required checks through repository settings; confirm the exact current head SHA and Actions conclusions; integrate one PR at a time; then refresh the next PR's base comparison and rerun its CI if its branch changes. Do not batch-merge all PRs based on historical CI. No PRs were merged or review approvals fabricated during this audit.


## Operational ownership and Last Chapter onboarding — 2026-10-24

**Scope boundary:** this portfolio workstream owns engineering governance only: repository instructions, agent handoffs, documentation, issue/PR templates, CI security, review gates, and read-only status reporting. Product UI, stories, gameplay, content, and product defects belong to each product's delivery workstream. An observed product CI failure may be recorded as a blocking dependency; do not fix product code or open product issues from this workstream without explicit direction.

### Last Chapter bootstrap acceptance — [draft PR #5](https://github.com/vlovers/last-chapter/pull/5)

The new repository has a minimal `main` README, and draft PR #5 proposes agent instructions, engineering docs, GitHub templates, and a pinned CI workflow **alongside product prototype files**. Treat the latter as product-owned; engineering review does not certify the game's narrative or implementation.

The exact-head `quality` run on `3ae5141f781cb36e272ce0f7be7c0ace5b131704` failed during Prettier: `src/main.ts:31` has an unescaped apostrophe in a single-quoted Ukrainian string; several files also fail formatting. The draft description acknowledges missing `package-lock.json`, temporary `npm install`, and incomplete verification. [Issue #1](https://github.com/vlovers/last-chapter/issues/1) is the toolchain/CI acceptance dependency. The implementation owner must address product-code syntax and formatting; governance only rechecks evidence.

**Review gates:** committed lockfile; CI uses `npm ci`; formatter, lint, typecheck, unit tests and build succeed on the **same head SHA**; pinned Actions and least-privilege permissions remain; `AGENTS.md`, security reporting, issue/PR templates and documentation agree; draft becomes ready only after author review. Do not merge while the draft is failing.

### Active CI observations, not blanket readiness

- [Grid Atlas #272](https://github.com/vlovers/grid-atlas/pull/272), head `80f7f414864c`: the new biography workflow is pinned and mergeability was observed as `true`, but the `visual-accessibility` job failed on Ukrainian `/constructors` at 200% font scaling in Chromium and WebKit. The product owner owns that regression; no UI/CSS changes belong in this CI-security PR. Other jobs were still running at the latest observation.
- [Portfolio #2](https://github.com/vlovers/vlovers/pull/2), head `fa1797ac7815`: added Last Chapter to the repository and foundation-PR inventory with a regression assertion; Actions were queued at the latest observation. Recheck after completion.

### Agent work handoff contract

For each agent task, record: **owner / repository / base branch / scoped paths / issue / acceptance criteria / required checks / dependencies / non-goals / handoff artifacts**. One agent owns each overlapping file set at a time. Agents must not merge, release, publish, delete branches, force-push, weaken checks, or change secrets without explicit authorization. An agent's `done` means evidence-backed PR readiness, not product acceptance or deployment. The coordinator tracks blockers and redirects product work to its owner rather than implementing it.


## GitHub branch governance audit — 2026-10-24

Read-only API inspection of repository rulesets, classic branch protection and default-branch `.github/CODEOWNERS`. **Do not infer that a 403 means protection is disabled.**

| Repository | Protected integration branch | Repository rulesets API | Classic branch protection API | CODEOWNERS at checked branch |
| --- | --- | --- | --- | --- |
| Grid Atlas | `main` | Empty list | 403 integration access denied | Not found |
| AI Office | `main` | Empty list | 403 integration access denied | Not found |
| RuleWitness | `main` | Active [Protect main ruleset](https://github.com/vlovers/rulewitness/rules/25238807) | 403 integration access denied | Not found |
| MutationBoundary | `main` | Empty list | 403 integration access denied | Not found |
| Estima | `develop` | Empty list | 403 integration access denied | Not found |
| Last Chapter | `main` | Empty list | 403 integration access denied | Not found |

**RuleWitness ruleset #25238807, verified by its detail endpoint:** default branch target; active enforcement; prevent deletion and non-fast-forward pushes; require PR; required check context `check` (integration id 15368); `required_approving_review_count: 0`, no code-owner approval, no last-push approval, no required thread resolution, non-strict status checks. No bypass actors are listed. Thus it enforces a PR and a check, **not independent approval**. Verify that the `check` context still corresponds to a currently running required job.

**Limits:** empty repository-ruleset lists do not exclude classic branch protection, organization-level policy, or other access controls. The integration cannot read classic protection (403). CODEOWNERS absence is based on the canonical `.github/CODEOWNERS` location only; check root `CODEOWNERS` and `docs/CODEOWNERS` before asserting no owners file exists anywhere.

**Owner decision needed before configuration writes:** choose review count (recommend at least one genuinely independent human approval where collaborators exist), stale-review dismissal/last-push approval, required thread resolution, and strict required checks. Validate exact job names from the live workflows before enforcing; an incorrect required check can deadlock all PRs. Preserve Estima's `develop` target. Enable settings only with explicit authorization and sufficient GitHub permissions; do not invent approvals or silently bypass required checks.

## Cross-project exact-head reconciliation — 2026-10-24 (latest governance check)

Rechecked the five still-open foundation PR heads, GitHub Actions runs and submitted reviews. The four source-repository PR descriptions were updated with run URLs; no source commits, merges or releases were made. The portfolio PR's own head will change when this audit is committed, so its previous green run must **not** be attributed to the new SHA.

| PR | Exact observed head | PR-triggered Actions evidence | Independent APPROVED submission |
| --- | --- | --- | --- |
| [MutationBoundary #68](https://github.com/vlovers/mutation-boundary/pull/68) | `d901cc88697a0e3008f866d32b6385f17342d52d` | [checks #40105239826](https://github.com/vlovers/mutation-boundary/actions/runs/40105239826): success | None observed; author COMMENTED |
| [RuleWitness #82](https://github.com/vlovers/rulewitness/pull/82) | `7ea6357de953a8cb9e37140dc2b67765f7941b5b` | [CI #40083577783](https://github.com/vlovers/rulewitness/actions/runs/40083577783), [permissions #40083577592](https://github.com/vlovers/rulewitness/actions/runs/40083577592): success | None observed; author COMMENTED |
| [Estima #13](https://github.com/vlovers/estima/pull/13) | `804873ea0b0c6311cce9dd7e883df1224ac93bfa` | [PostgreSQL #40081427792](https://github.com/vlovers/estima/actions/runs/40081427792), [Bun #40081427815](https://github.com/vlovers/estima/actions/runs/40081427815): success | None observed; author COMMENTED |
| [AI Office #43](https://github.com/vlovers/ai-office/pull/43) | `3eb4eaae2b8c7af7e788d1d4feb14602e0d7ea92` | [validation #40105333564](https://github.com/vlovers/ai-office/actions/runs/40105333564): success | None observed; author COMMENTED |
| [Portfolio #2](https://github.com/vlovers/vlovers/pull/2) | `b0618462e500a0b116e5c6f30940c611ced83ced` (pre-edit) | [validation #40121960041](https://github.com/vlovers/vlovers/actions/runs/40121960041): success on **pre-edit head** | None observed |

**Grid Atlas #272 separate blocker:** on `1c22563d0ec0de332e5bfd2082e74f6108cf3350`, [Unified archive experience #40110810456](https://github.com/vlovers/grid-atlas/actions/runs/40110810456) failed and [Next.js web #40110810392](https://github.com/vlovers/grid-atlas/actions/runs/40110810392) was cancelled. Do not report this PR as 9/9 green, even if another branch or an earlier SHA had a clean run. Keep the browser accessibility gate intact and coordinate with the product owner.

**Merge gate:** these observations do not establish reviewer independence, enforced required checks, absence of conflicts, or permission to merge. All five still-open foundation PRs await independent acceptance and maintainer authorization. The portfolio docs edit requires a fresh CI result on its resulting head.
