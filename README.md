# Mikhail Kohut

**Full-stack Software Engineer** · TypeScript · React / Next.js · Node.js / NestJS

I build full-stack products and open-source developer tools, with an emphasis on dependable APIs, PostgreSQL, security boundaries, testing, and clear engineering trade-offs. Recently I've been working on coding-agent workflows, permission analysis, and data-rich interactive products.

Based in Ukraine · Open to remote engineering roles and open-source collaboration.

## Selected projects

| Project | What it does | Status |
| --- | --- | --- |
| **[Grid Atlas](https://github.com/vlovers/grid-atlas)** | Source-backed Formula 1 historical encyclopedia with bilingual driver, constructor, circuit, season and race exploration, plus an evidence-based historical network. | Public beta in preparation |
| **[AI Office](https://github.com/vlovers/ai-office)** | Local-first Codex workspace with two workers, reusable agent profiles, isolated Git worktrees, task streaming, and explicit review / keep / reject workflows. | [v0.5.0 released](https://github.com/vlovers/ai-office/releases/tag/v0.5.0); v0.6.0 implementation integrated, not yet released |
| **[RuleWitness](https://github.com/vlovers/rulewitness)** | Offline TypeScript CLI that detects modeled permission-decision changes in supported Claude Code rules across Git revisions, with concrete witnesses and policy assertions. | [v0.3.0 on npm](https://www.npmjs.com/package/rulewitness/v/0.3.0) |
| **[MutationBoundary](https://github.com/vlovers/mutation-boundary)** | PostgreSQL test utility for detecting unexpected committed row changes after failed or supposedly read-only operations. | v0.3.0 release candidate; [npm package](https://www.npmjs.com/package/mutation-boundary) |
| **[Estima](https://github.com/vlovers/estima)** | Full-stack AI-assisted software estimation with task management, feedback calibration, JWT authentication, migrations and PostgreSQL integration tests. | Active development |

### What makes these projects interesting

- **AI agent safety and review:** RuleWitness models *configuration-rule* changes, not runtime authorization; AI Office defaults to read-only and requires explicit authorization for isolated write tasks.
- **Data correctness:** MutationBoundary checks a focused database invariant; Estima exercises migrations and API behavior against PostgreSQL.
- **Evidence-driven interfaces:** Grid Atlas combines historical F1 datasets with separately reviewed lineage evidence. Its public beta and hosting are still in progress.

## Tech I work with

| Area | Technologies |
| --- | --- |
| Frontend | TypeScript, React, Next.js, TanStack Query |
| Backend | Node.js, NestJS, Fastify, REST APIs, GraphQL |
| Data | PostgreSQL, SQLite, MongoDB, TypeORM |
| Tooling | Docker, GitHub Actions, Git, automated tests, Nx |
| Current interests | Developer experience, AI coding agents, application security, historical-data visualization |

## Get in touch

Interested in **remote full-stack engineering**, open-source collaboration, and building reliable developer tools.

[Explore my repositories](https://github.com/vlovers?tab=repositories) · [RuleWitness on npm](https://www.npmjs.com/package/rulewitness) · [MutationBoundary on npm](https://www.npmjs.com/package/mutation-boundary)

<sub>Project descriptions reflect the documented repository status. Experimental tools have explicit scope and limitations; in-development projects are not presented as production deployments.</sub>
