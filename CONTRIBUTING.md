# Contributing

The workflow is deliberately strict — the process is part of what this repository
demonstrates.

## Workflow

Every change, including documentation, ships as a **merged pull request** tied to a ticket
from [docs/IMPLEMENTATION_PLAN.md](./docs/IMPLEMENTATION_PLAN.md).

```bash
git switch main && git pull --ff-only
git switch -c feat/T-203-api-client
# work, commit, push
gh pr create --fill --base main
gh pr merge --squash --delete-branch
```

## Branch naming

`<type>/<ticket-id>-<short-slug>` — for example `feat/T-206-project-detail`,
`fix/T-105-rate-limit-window`, `docs/T-301-content-guide`.

Types: `feat`, `fix`, `chore`, `docs`, `test`, `refactor`, `ci`, `perf`.

## Commits

[Conventional Commits](https://www.conventionalcommits.org/), with the ticket id in the
subject:

```
feat(api): contact endpoint with rate limiting and honeypot (T-105)
fix(web): abort in-flight requests on unmount (T-203)
docs(architecture): record the SPA/SEO trade-off (T-001)
```

Scopes: `web`, `api`, `content`, `infra`, `docs`, `ci`.

## Before pushing

```bash
make check     # lint + typecheck + unit tests, both apps
```

A push that fails CI is a broken window. Run `make check` locally first.

## Definition of Done

Every ticket must satisfy the full checklist in
[docs/IMPLEMENTATION_PLAN.md § 1](./docs/IMPLEMENTATION_PLAN.md#1-how-a-ticket-is-worked).
The parts most often skipped, and therefore worth repeating:

- Tests for new logic, not just for the happy path
- `PROGRESS.md` updated in the same PR
- No new lint or type suppressions without a comment explaining why
- No secrets, credentials or personal data committed

## Code conventions

**TypeScript / Vue**
- `<script setup lang="ts">`, Composition API, no Options API
- Props and emits are explicitly typed; no `any` (use `unknown` and narrow)
- Components are presentational; data fetching belongs in views or composables
- Colours, spacing and typography come from design tokens — never literal hex values

**Python**
- Full type annotations; `mypy --strict` must pass
- Routers parse and delegate; business rules live in services; queries live in repositories
- Public functions get a docstring only when the name is not enough
- No bare `except:`; catch specific exceptions and log with context

**Both**
- Comments explain *why*, never *what*
- A function that needs a comment to explain what it does usually needs a better name

## Adding a project to the portfolio

Content is code. See [content/README.md](./content/README.md) — add a Markdown file, run
`make seed --check`, open a PR.
