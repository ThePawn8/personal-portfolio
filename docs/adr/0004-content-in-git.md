# ADR-0004 — Project content lives in git and is seeded into MongoDB

- Status: Accepted
- Date: 2026-08-26

## Context

Project descriptions, links and mockup references must be authored, reviewed and changed
over time. They could live only in the database, be edited through an admin UI, or be
authored as files in the repository.

## Decision

Author each project as `content/projects/<slug>.md` — YAML frontmatter plus a Markdown case
study — and load it into MongoDB with an idempotent seed command (upsert by `slug`) that
runs in CI on merge to `main`.

## Consequences

- Content changes are pull requests: reviewable, revertable, with full history.
- A malformed project fails Pydantic validation in CI and never reaches production.
- The database is reproducible from the repository, which downgrades "lost the volume" from
  a data-loss incident to a re-run of `make seed`.
- The seed is additive: it never deletes. Retiring a project means `published: false`, so a
  removed file cannot silently wipe a document.
- **Accepted cost:** editing content requires a commit and a deploy, not a text box. For a
  site updated roughly monthly this is a feature, not friction.

## Alternatives rejected

- **Authenticated admin UI:** demonstrates auth and CRUD, but adds sessions, password
  handling, an authorisation matrix and a permanent attack surface to a single-author site.
- **Editing documents directly in the database:** no history, no review, no reproducibility.
