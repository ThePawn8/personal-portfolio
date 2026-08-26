# Personal Portfolio

A production-grade personal portfolio: a **Vue 3 + TypeScript** single-page application
backed by a **FastAPI + MongoDB** service, deployed on Vercel and Fly.io.

The site presents professional experience and project case studies. The repository itself is
part of the work sample — architecture decisions, tests, quality gates and deployment
pipeline are meant to be read.

| | |
|---|---|
| **Live site** | _not deployed yet_ |
| **API** | _not deployed yet_ |
| **Architecture** | [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) |
| **Plan and tickets** | [docs/IMPLEMENTATION_PLAN.md](./docs/IMPLEMENTATION_PLAN.md) |
| **Current status** | [PROGRESS.md](./PROGRESS.md) |

---

## Stack

| Layer | Technology |
|---|---|
| Frontend | Vue 3.5 (Composition API), Vite 8, TypeScript strict, Tailwind v4, Pinia, vue-router |
| Backend | FastAPI, Python 3.12, Beanie (Pydantic v2) over Motor, structlog |
| Database | MongoDB 7 |
| Testing | Vitest, @vue/test-utils, Playwright + axe-core, pytest, httpx |
| Quality | ESLint, Prettier, Ruff, mypy strict, coverage gates, gitleaks |
| Infrastructure | Vercel (web), Fly.io (API + MongoDB), GitHub Actions |

---

## Repository layout

```
.
├── apps/
│   ├── web/          Vue 3 SPA
│   └── api/          FastAPI service
├── content/          Project case studies and profile data (source of truth)
├── docs/             Architecture, implementation plan, ADRs, runbook
├── infra/            docker-compose, Fly.io configuration
└── .github/          CI/CD workflows and repository automation
```

Content lives in git and is seeded into MongoDB — see
[ADR-0004](./docs/adr/0004-content-in-git.md).

---

## Getting started

**Prerequisites:** Node 24 (see `.nvmrc`), Python 3.12, Docker Desktop (for local MongoDB),
and [uv](https://docs.astral.sh/uv/) (`pip install uv`).

```bash
git clone https://github.com/ThePawn8/personal-portfolio.git
cd personal-portfolio
cp .env.example .env          # then fill in the values

make install                  # install web and API dependencies
make db-up                    # start MongoDB in Docker
make seed                     # load content/ into MongoDB
make dev                      # API on :8000, web on :5173
```

Without Docker, point `MONGODB_URI` at any reachable MongoDB instance and skip `make db-up`.

### Commands

`make` is not available on Windows by default, so every target has an identical npm script.
Use whichever your shell has.

| Task | make | npm |
|---|---|---|
| Run API and web together | `make dev` | `npm run dev` |
| Run one side only | `make dev-web` / `make dev-api` | `npm run dev:web` / `npm run dev:api` |
| Lint, typecheck, unit tests (both apps) | `make check` | `npm run check` |
| All tests with coverage | `make test` | `npm run test` |
| End-to-end suite | `make e2e` | `npm run e2e` |
| Load `content/` into MongoDB | `make seed` | `npm run seed` |
| Validate content without writing | `make seed-check` | `npm run seed:check` |
| Start / stop local MongoDB | `make db-up` / `make db-down` | `npm run db:up` / `npm run db:down` |

Run `npm run check` before every push — it is exactly what CI runs.

Each app also exposes its own scripts directly: `npm run …` in `apps/web`, `uv run …` in
`apps/api`.

---

## Contributing

This is a personal project, but it follows a strict workflow: one ticket, one branch, one
pull request, squash-merged with CI green. See [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

[MIT](./LICENSE) for the code. Written content, images and CV are © Andrés M, all rights
reserved.
