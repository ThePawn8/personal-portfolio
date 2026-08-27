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
| Backend | FastAPI, Python 3.12, Beanie 2 (Pydantic v2 over async pymongo), structlog |
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

**Prerequisites:** Node 24 (see `.nvmrc`), Python 3.12, [uv](https://docs.astral.sh/uv/)
(`pip install uv`), and a MongoDB 7 to talk to — Docker Desktop is the easy route, but see
[Without Docker](#without-docker) if you would rather not install it.

```bash
git clone https://github.com/ThePawn8/personal-portfolio.git
cd personal-portfolio

npm run setup         # create .env and generate local secrets
npm run install:all   # web and API dependencies
npm run db:up         # MongoDB in Docker
npm run seed          # load content/ into MongoDB
npm run dev           # API on :8000, web on :5173
```

Open <http://localhost:5173> for the site and <http://localhost:8000/docs> for the API
contract.

The local database runs with authentication enabled and the API connects as a
least-privilege user (`readWrite` on one database), matching production. Those credentials
are local-only and deliberately committed; real secrets live in `fly secrets` and GitHub
Actions secrets.

### Without Docker

Point `MONGODB_URI` in `.env` at any reachable MongoDB 7 instance and skip `npm run db:up`.
A free MongoDB Atlas cluster works, and so does a local `mongod`.

If you have neither, this starts a real MongoDB with no Docker and no system install — it
downloads a `mongod` binary into a cache directory and runs it on the usual port:

```bash
mkdir -p /tmp/mongo-dev && cd /tmp/mongo-dev
npm init -y && npm install mongodb-memory-server

cat > start.mjs <<'EOF'
import { MongoMemoryServer } from 'mongodb-memory-server'
const server = await MongoMemoryServer.create({
  instance: { port: 27017, dbName: 'portfolio' },
  binary: { version: '7.0.14' },
})
console.log('ready:', server.getUri())
setInterval(() => {}, 1 << 30)
EOF

node start.mjs
```

Single node, exactly like production ([ADR-0003](./docs/adr/0003-mongodb-self-hosted.md)), so
the absence of multi-document transactions is consistent everywhere. It runs without
authentication, so set `MONGODB_URI=mongodb://127.0.0.1:27017` in `.env` for that setup.

### Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `docker: command not found` | Docker Desktop is not installed or not running |
| API cannot authenticate to MongoDB | The init script only runs on an empty volume. `npm run db:reset` recreates it |
| Port 27017 already in use | Another MongoDB is running locally. Stop it, or change the published port in `infra/docker-compose.yml` |
| `uv: command not found` | `pip install uv` |
| `make: command not found` | Expected on Windows — use the npm equivalents below |

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
