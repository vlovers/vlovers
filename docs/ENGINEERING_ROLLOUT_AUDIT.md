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
| [AI Office #43](https://github.com/vlovers/ai-office/pull/43) | `304f0e9b86e8` | AI Office validation success |
| [RuleWitness #82](https://github.com/vlovers/rulewitness/pull/82) | `124e45efd403` | CI + permissions review success |
| [MutationBoundary #68](https://github.com/vlovers/mutation-boundary/pull/68) | `ca8783f92896` | MutationBoundary checks success |
| [Estima #13](https://github.com/vlovers/estima/pull/13) | `d02560c79215` | Bun + PostgreSQL integration success |
| [Portfolio #2](https://github.com/vlovers/vlovers/pull/2) | moving head | Previous CI successful; new review-evidence tests require fresh CI on final commit |

All five still-open baseline PRs require independent review and maintainer acceptance. A historical success does not apply after a new push.

## Independent-review gate — observed 2026-10-24

The five open foundation PRs [MutationBoundary #68](https://github.com/vlovers/mutation-boundary/pull/68), [RuleWitness #82](https://github.com/vlovers/rulewitness/pull/82), [Estima #13](https://github.com/vlovers/estima/pull/13), [AI Office #43](https://github.com/vlovers/ai-office/pull/43) and [Portfolio #2](https://github.com/vlovers/vlovers/pull/2) have successful observed PR Actions on the SHAs checked. **No independent approval was confirmed**: the first four have only author-account COMMENTED technical assessments in the reviewed submissions, and Portfolio #2 had no review submissions. The AI Office review comments also flag possible branch divergence; current GitHub PR metadata reports `mergeable=true`, but that alone cannot resolve the reviewer-requested branch integration and sandbox acceptance. A fresh review of the final diff, branch rules and latest CI SHA is still required. Do not merge based on this audit.

The portfolio report now exposes read-only review observations separately from Actions evidence. It rejects incomplete review pagination, ignores author and bot approvals, treats historical/dismissed approvals as insufficient, and reports outstanding change requests. **Even a current-head approval from another account is not certification of independence or branch-rule compliance.** Do not infer maintainer acceptance or merge authorization from this table or script.

## Intake and CI hardening queue — verified 2026-10-24

These are **separate open PRs**, not deployed default-branch changes. CI observations were rechecked 2026-10-24; refresh before relying on them. Keep acceptance and release states distinct.

| Repository | Intake / contributor PR | CI supply-chain PR | Last observed CI state |
| --- | --- | --- | --- |
| Grid Atlas | [#271](https://github.com/vlovers/grid-atlas/pull/271) | [#272](https://github.com/vlovers/grid-atlas/pull/272) | #271 Foundation CI passed. **#272 has 9/9 successful workflows** on head `4aeab9b78c81` after the targeted narrow-viewport `/constructors` fix (previously 7/9) |
| AI Office | [#48](https://github.com/vlovers/ai-office/pull/48) | [#49](https://github.com/vlovers/ai-office/pull/49) | Both validation runs passed on respective head SHAs |
| RuleWitness | [#83](https://github.com/vlovers/rulewitness/pull/83) | Existing pinned and read-only CI | CI + permissions review passed on #83 head |
| MutationBoundary | [#69](https://github.com/vlovers/mutation-boundary/pull/69) | [#70](https://github.com/vlovers/mutation-boundary/pull/70) | #69 and #70 checks passed on respective head SHAs; #70 release guard not deployed |
| Estima | [#14](https://github.com/vlovers/estima/pull/14) | [#15](https://github.com/vlovers/estima/pull/15) | PostgreSQL + Bun workflows passed on both heads; CI hardening not merged |

**Integration rule:** before opening another broad standardization PR, finish the existing queue or document a verified blocker. The PR author cannot self-certify independence simply by running another prompt. Confirm real repository rulesets and approvals through GitHub settings or an authorized reviewer; current GitHub connector does not expose branch protection settings. For AI Office, check whether PR branches diverged since last verified run, and do not apply stale green CI to a new SHA.

**Review focus:** malformed GitHub Issue YAML front matter, reporter security guidance, duplicate template options, unpinned third-party actions, persistent checkout credentials and CI on the exact final head. Resolve with narrow commits to the current PR branches; do not mass-close Issues or auto-merge.
