# ADR-0002 — Vue SPA (Vite) instead of Nuxt SSR/SSG

- Status: Accepted
- Date: 2026-08-26

## Context

A portfolio must be indexable and shareable. Nuxt would deliver SSR/SSG and per-route social
previews out of the box; a plain Vite SPA ships static HTML with a client-rendered body.

## Decision

Build a Vue 3 + Vite SPA. Chosen by the author to keep the codebase "plain Vue" — the skill
being demonstrated is Vue itself, not a meta-framework.

## Consequences

- **Accepted cost:** LinkedIn, WhatsApp, Slack and X do not execute JavaScript, so deep
  links to a project show the site-wide Open Graph card, not that project's own preview.
  For a portfolio shared mostly on LinkedIn, this is the sharpest trade-off in the project.
- Google renders JavaScript and will index the content, so organic search is not blocked.
- Mitigations in v1: rich static meta and an OG image in `index.html`, per-route `<head>`
  via `@unhead/vue`, generated `sitemap.xml` and `robots.txt`.
- The escape hatch is kept cheap: routes stay data-driven and free of browser-only globals
  at module scope, so adding `vite-ssg` prerendering later is a build-config change rather
  than a rewrite (T-503).

## Alternatives rejected

- **Nuxt 4:** strictly better SEO, but adds a framework layer between the author and Vue.
- **vite-ssg from day one:** prerendering requires the content to exist at build time, which
  couples the web build to a reachable API. Deferred until content has stabilised.
