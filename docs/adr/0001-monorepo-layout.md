# ADR-0001 — Single repository with apps/web and apps/api

- Status: Accepted
- Date: 2026-08-26

## Context

The portfolio is one product built from two deployables: a Vue SPA and a FastAPI service.
They share a contract (the JSON API), a release cadence and one author.

## Decision

Keep both in a single repository under `apps/web` and `apps/api`, with shared content in
`content/`, infrastructure in `infra/` and documentation in `docs/`. No monorepo tooling
(Nx, Turborepo) — a `Makefile` orchestrates the two toolchains.

## Consequences

- A contract change and its consumer land in the **same pull request**, so the API and the
  UI can never drift between commits.
- One CI workflow with path filters; `apps/web` changes do not run pytest.
- The repository is the portfolio artefact a reviewer opens — one link shows everything.
- Cost: CI needs both toolchains (Node + Python) available; jobs are split so each installs
  only what it needs.

## Alternatives rejected

- **Two repositories:** more realistic for a team, but doubles CI setup, splits the review
  history and gives a visitor two links to open instead of one.
- **Nx / Turborepo:** caching and task graphs solve a problem that two packages do not have.
