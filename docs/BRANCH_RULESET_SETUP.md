# Branch protection setup — six-project portfolio

Status: **proposed, not applied**. Owner action required in GitHub UI. Updated 2026-10-24.

| Repository | Branch | Owner action |
| --- | --- | --- |
| [Grid Atlas](https://github.com/vlovers/grid-atlas/settings/rules) | `main` | Create rule after checking classic protection |
| [AI Office](https://github.com/vlovers/ai-office/settings/rules) | `main` | Create rule after checking classic protection |
| [RuleWitness](https://github.com/vlovers/rulewitness/settings/rules) | `main` | **Edit existing** [Protect main](https://github.com/vlovers/rulewitness/rules/25238807) |
| [MutationBoundary](https://github.com/vlovers/mutation-boundary/settings/rules) | `main` | Create rule after checking classic protection |
| [Estima](https://github.com/vlovers/estima/settings/rules) | `develop` | Protect `develop`; assess `main` separately |
| [Last Chapter](https://github.com/vlovers/last-chapter/settings/rules) | `main` | Create rule after checking classic protection |

Classic branch protection API returned **403** on all six projects; this means **unknown**, not disabled. Five repository-ruleset lists were empty. RuleWitness has one active ruleset. No CODEOWNERS found in `.github/`, repository root or `docs/` on the checked integration branches.

## Owner UI procedure

1. Open the repository link above → **Settings → Rules → Rulesets**. Choose **New branch ruleset** except for RuleWitness, where the existing ruleset must be edited.
2. Name the rule `Protect integration branch`. Target only the branch shown in the table; do not accidentally target all feature branches.
3. Enable **Restrict deletions**, **Block force pushes**, **Require a pull request before merging**.
4. For **Require status checks to pass**, first identify **exact check context names** from a recent successful PR on that branch. Workflow filenames are not check contexts. Ensure every required check runs for normal PRs and is not routinely skipped. Never guess the check name or turn on an unverified required check.
5. Enable **Require conversation resolution before merging** if available. Set **one approval** only when an independent reviewer is actually available; solo projects otherwise risk deadlock. Agent comments and self-approval are not independent review.
6. Consider dismissing stale approvals or last-push approval after testing the review workflow. Decide whether up-to-date branches should be mandatory based on CI cost.
7. Inspect bypass actors, verify branch target and checks, and save only after a rollback plan. If GitHub plan limitations prevent enforcement, record the limitation.
8. Verify with a harmless documentation PR that passing checks are recognized, failing checks block merging, and direct pushes/deletions are rejected. Record rule URL, check contexts and date.

## RuleWitness existing rule

Ruleset #25238807 is active on the default branch; it blocks deletion and non-fast-forward updates, requires PRs and status context `check` (integration 15368). It requires **zero** approving reviews, does not require resolved review threads or last-push approval, and has non-strict checks. Confirm that `check` is still produced by current CI before modifying. Never remove an existing protection before replacement.

## Scope and authorization

This guide does **not** authorize modifying GitHub settings, merging PRs, publishing, deleting branches or granting secrets. Engineering governance tracks evidence and coordinates product owners; it does not change product code. The GitHub connector lacks Administration scope, so settings changes must be performed by the repository owner in the UI or another explicitly authorized administrative integration.
