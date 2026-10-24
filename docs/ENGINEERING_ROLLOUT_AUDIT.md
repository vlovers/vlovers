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
