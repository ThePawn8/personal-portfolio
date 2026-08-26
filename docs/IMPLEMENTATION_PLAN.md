# Implementation Plan — Personal Portfolio

> Companion to [ARCHITECTURE.md](./ARCHITECTURE.md). Live status lives in
> [../PROGRESS.md](../PROGRESS.md) — this file describes *what* the work is, PROGRESS.md
> records *where it stands*.

---

## 1. How a ticket is worked

Every ticket ends as a **merged pull request**. No exceptions, including documentation.

```bash
git switch main && git pull --ff-only
git switch -c feat/T-203-api-client          # branch = <type>/<ticket-id>-<slug>
# ... work ...
git commit -m "feat(web): typed API client with fallback snapshot (T-203)"
git push -u origin feat/T-203-api-client
gh pr create --fill --base main
# CI green -> review -> squash merge
gh pr merge --squash --delete-branch
```

**Branch prefixes:** `feat/`, `fix/`, `chore/`, `docs/`, `test/`, `refactor/`, `ci/`.
**Commits:** [Conventional Commits](https://www.conventionalcommits.org/), scope is
`web` / `api` / `content` / `infra` / `docs`, ticket id in the subject.
**Merge strategy:** squash — one ticket, one commit on `main`.

### Definition of Ready

A ticket may start only when: its dependencies are merged, its acceptance criteria are
unambiguous, and any content or credential it needs is available.

### Definition of Done (applies to every ticket)

- [ ] Acceptance criteria met
- [ ] Tests written for new logic and passing locally
- [ ] `make check` passes (lint + typecheck + unit tests, both apps)
- [ ] No new lint/type suppressions without an inline comment justifying them
- [ ] No secrets, credentials or personal data added to the repo
- [ ] Documentation updated when behaviour or setup changed (README / ARCHITECTURE / ADR)
- [ ] `PROGRESS.md` updated: ticket moved to Done, notes and follow-ups recorded
- [ ] CI green on the PR
- [ ] PR squash-merged and branch deleted

---

## 2. Sizing

| Size | Meaning | Rough effort |
|---|---|---|
| S | One file or one focused change | ≤ 1 h |
| M | Several files, tests included | 2–4 h |
| L | A subsystem; consider splitting if it grows | 5–8 h |

---

## 3. Parallelisation waves

Tickets in the same wave touch disjoint files and can be worked in parallel — in separate
sessions, separate branches, or by separate agents. Tickets in later waves depend on
earlier ones.

```mermaid
graph LR
    subgraph W0["Wave 0 - bootstrap"]
        T001["T-001 repo + docs"]
    end
    subgraph W1["Wave 1 - scaffolds (parallel)"]
        T002["T-002 web scaffold"]
        T003["T-003 api scaffold"]
        T005["T-005 local dev env"]
        T301["T-301 content schema"]
    end
    subgraph W2["Wave 2 - foundations (parallel)"]
        T004["T-004 CI"]
        T101["T-101 config/logging/errors"]
        T201["T-201 design system"]
        T302["T-302 profile content"]
    end
    subgraph W3["Wave 3"]
        T102["T-102 mongo + models"]
        T202["T-202 app shell"]
        T303["T-303 case studies"]
        T304["T-304 mockups"]
    end
    subgraph W4["Wave 4 - feature build-out"]
        T103["T-103 projects API"]
        T105["T-105 contact API"]
        T107["T-107 seed command"]
        T203["T-203 api client"]
        T401["T-401 api image"]
        T402["T-402 mongo on fly"]
    end
    subgraph W5["Wave 5 - pages + deploy"]
        T104["T-104 profile API"]
        T106["T-106 email"]
        T204["T-204 home"]
        T205["T-205 projects index"]
        T206["T-206 project detail"]
        T207["T-207 about"]
        T208["T-208 contact page"]
        T403["T-403 vercel"]
        T404["T-404 deploy workflows"]
    end
    subgraph W6["Wave 6 - hardening + launch"]
        T108["T-108 contract test"]
        T209["T-209 SEO"]
        T210["T-210 images"]
        T405["T-405 smoke + uptime"]
        T501["T-501 e2e + a11y"]
        T502["T-502 perf budgets"]
        T505["T-505 security"]
        T506["T-506 launch"]
    end

    W0 --> W1 --> W2 --> W3 --> W4 --> W5 --> W6
```

**The critical path to a live site** is: T-001 → T-003 → T-101 → T-102 → T-103 → T-107 →
T-401 → T-402 → T-403 → T-404. Everything else can slip without delaying launch.

---

## 4. Epic 0 — Foundations

### T-001 · Repository bootstrap and documentation · S · no deps

Initialise the repository with its documentation, conventions and hygiene files.

**Scope:** `.gitignore`, `.editorconfig`, `.gitattributes`, `.nvmrc`, `LICENSE`, `README.md`,
`docs/ARCHITECTURE.md`, `docs/IMPLEMENTATION_PLAN.md`, `docs/adr/000*.md`, `PROGRESS.md`,
`CONTRIBUTING.md`, `.github/PULL_REQUEST_TEMPLATE.md`, `.github/dependabot.yml`, `Makefile`,
`.env.example`; GitHub repository created and `main` pushed.

**Acceptance criteria**
- [ ] Repository exists on GitHub, `main` is the default branch
- [ ] Architecture, plan, ADRs and progress documents are readable on GitHub (mermaid renders)
- [ ] `README.md` explains what the project is and how to run it
- [ ] Branch protection on `main`: PR required, CI required, no direct pushes

---

### T-002 · Web application scaffold and tooling · M · deps: T-001

Vue 3 + Vite + TypeScript application with the full quality toolchain, no features yet.

**Scope:** Vite + `@vitejs/plugin-vue`, TS strict with `@/*` path alias, ESLint flat config
(vue + typescript-eslint + prettier interop), Prettier, Vitest + jsdom + coverage thresholds,
Playwright config, npm scripts (`dev`, `build`, `typecheck`, `lint`, `test`, `e2e`).

**Acceptance criteria**
- [ ] `npm run dev` serves a page, `npm run build` produces a bundle
- [ ] `npm run typecheck`, `npm run lint`, `npm run test` all pass with zero warnings
- [ ] Coverage thresholds configured (80/80/75/80) and enforced
- [ ] One smoke unit test and one smoke e2e test exist and pass

---

### T-003 · API application scaffold and tooling · M · deps: T-001 · ∥ T-002

FastAPI project skeleton with packaging, linting, typing and test harness.

**Scope:** `uv` + `pyproject.toml`, package layout from ARCHITECTURE § 6.2, Ruff (lint +
format), mypy `--strict`, pytest + pytest-asyncio + httpx, coverage gate, `/healthz`,
`uvicorn` entry point.

**Acceptance criteria**
- [ ] `uv sync` installs a locked, reproducible environment
- [ ] `uv run uvicorn` serves `/healthz` returning `{"status": "ok"}`
- [ ] `ruff check`, `ruff format --check`, `mypy --strict` all clean
- [ ] `pytest --cov-fail-under=80` passes with a test for `/healthz`

---

### T-004 · CI pipeline · M · deps: T-002, T-003

GitHub Actions running every quality gate on every PR, with path filters so each job runs
only when it is relevant.

**Scope:** `.github/workflows/ci.yml` with jobs `web-quality`, `api-quality`, `e2e`,
`security` (gitleaks, npm audit, pip-audit); dependency caching; Mongo service container for
API integration tests; required status checks configured on `main`.

**Acceptance criteria**
- [ ] A PR touching only `apps/web` does not run the API job (and vice versa)
- [ ] All jobs pass on a clean PR in under ~5 minutes
- [ ] A deliberately broken lint rule or failing test blocks the merge (verified once)
- [ ] Dependabot configured for npm, pip and GitHub Actions

---

### T-005 · Local development environment · S · deps: T-001 · ∥ T-002, T-003

One command to run the whole stack locally.

**Scope:** `infra/docker-compose.yml` (MongoDB 7 with a named volume and healthcheck),
root `Makefile` (`dev`, `dev-web`, `dev-api`, `check`, `test`, `seed`, `db-up`, `db-down`),
`.env.example` documenting every variable, README setup section.

**Acceptance criteria**
- [ ] `make db-up && make dev` brings up Mongo, API and web from a clean clone
- [ ] Every environment variable the apps read appears in `.env.example`
- [ ] README documents the Docker Desktop prerequisite and a no-Docker fallback

---

## 5. Epic 1 — Backend

### T-101 · Configuration, logging and error contract · M · deps: T-003

**Scope:** `core/config.py` (pydantic-settings, fail-fast validation), `core/logging.py`
(structlog JSON + request-id contextvar), request-id middleware emitting `X-Request-ID`,
`core/errors.py` (domain exceptions + RFC 9457 handlers for HTTPException, validation errors
and unhandled exceptions), CORS middleware driven by settings.

**Acceptance criteria**
- [ ] Missing required settings abort startup with a clear message, not a 500 at runtime
- [ ] Every response carries `X-Request-ID`; the same id appears in the log line
- [ ] 404, 422 and 500 all return `application/problem+json` matching ADR-0005
- [ ] Unhandled exceptions never leak a stack trace to the client, and always log one
- [ ] Tests cover each handler and the CORS allowlist

---

### T-102 · MongoDB connection, models and indexes · M · deps: T-101

**Scope:** Motor client + Beanie init in the app lifespan, `Project` / `Message` /
`RateLimitBucket` documents per ARCHITECTURE § 7, index declarations (including the TTL
index), `/readyz` pinging Mongo, pytest fixtures providing a clean database per test.

**Acceptance criteria**
- [ ] App connects on startup and closes the pool on shutdown
- [ ] Indexes are created on boot and verified by a test reading `index_information()`
- [ ] `/readyz` returns 503 with problem+json when Mongo is unreachable
- [ ] Integration tests run against a real Mongo container, isolated per test

---

### T-103 · Projects API · M · deps: T-102

**Scope:** `ProjectRepository` (all queries), `ProjectService`, `GET /api/v1/projects`
(published only, sorted by `featured` then `order`, optional `tag` filter) and
`GET /api/v1/projects/{slug}`, response schemas separate from documents, `Cache-Control`
plus ETag/`If-None-Match` handling.

**Acceptance criteria**
- [ ] Unpublished projects are never returned by either endpoint
- [ ] Unknown slug returns 404 problem+json with `type` `project-not-found`
- [ ] A repeated request with `If-None-Match` returns 304 with an empty body
- [ ] Sort order and `tag` filtering covered by integration tests

---

### T-104 · Profile API · S · deps: T-102, T-107

**Scope:** `GET /api/v1/profile` returning bio, experience, education, skills and CV link,
seeded from `content/profile.yml`.

**Acceptance criteria**
- [ ] Response matches the documented schema and is cached for 5 minutes
- [ ] Experience entries are returned newest-first
- [ ] Missing profile document returns 404 problem+json rather than an empty object

---

### T-105 · Contact API · M · deps: T-102

**Scope:** `POST /api/v1/contact` with Pydantic validation (name 2–80, valid email, body
10–4000), honeypot field silently accepted-and-dropped, fixed-window rate limiter (5/hour/IP)
backed by the TTL collection, SHA-256 IP hashing, persistence, `202 Accepted`.

**Acceptance criteria**
- [ ] Valid submission returns 202 and persists exactly one message
- [ ] Invalid payloads return 422 problem+json naming the offending field
- [ ] The sixth submission within an hour returns 429 with a `Retry-After` header
- [ ] A filled honeypot returns 202 but persists nothing
- [ ] No raw IP address is ever written to the database (asserted in a test)

---

### T-106 · Email notification via Resend · S · deps: T-105

**Scope:** `EmailService` calling the Resend API in a background task, message status
transitions (`received` → `notified` / `failed`), timeout and one retry, injectable fake for
tests, graceful no-op when the API key is unset (local development).

**Acceptance criteria**
- [ ] A successful submission triggers exactly one email and sets status `notified`
- [ ] Email failure does not fail the request; status becomes `failed` and an error is logged
- [ ] No network call is made in tests
- [ ] Missing `RESEND_API_KEY` logs a warning at startup instead of crashing

---

### T-107 · Content seed command · M · deps: T-102

**Scope:** `python -m portfolio_api.seed` parsing `content/projects/*.md` (YAML frontmatter +
Markdown body) and `content/profile.yml`, validating against Pydantic schemas, rendering
Markdown to sanitised HTML, upserting by `slug`, `--dry-run` and `--check` modes.

**Acceptance criteria**
- [ ] Running the seed twice produces no changes the second time (idempotent)
- [ ] An invalid or incomplete file exits non-zero naming the file and the field
- [ ] `--check` validates without writing (used as a CI gate on content PRs)
- [ ] Rendered HTML is sanitised — a `<script>` in Markdown does not survive (test)
- [ ] Removing a file never deletes a document

---

### T-108 · OpenAPI contract snapshot test · S · deps: T-103, T-105

**Scope:** committed `openapi.snapshot.json` and a test comparing the generated schema
against it, with a documented one-line update command.

**Acceptance criteria**
- [ ] Changing a response model without updating the snapshot fails CI
- [ ] The failure message explains how to regenerate the snapshot

---

## 6. Epic 2 — Frontend

### T-201 · Design system and tokens · M · deps: T-002

**Scope:** Tailwind v4 `@theme` mapped to semantic CSS variables (background, surface, text,
muted, accent, border), light and dark palettes, type scale, spacing and radii, focus-visible
ring, `prefers-reduced-motion` handling, and base components: `BaseButton`, `BaseBadge`,
`BaseCard`, `AppContainer`, `SectionHeading`.

**Acceptance criteria**
- [ ] Every colour used in the app is a token; no literal hex values in components
- [ ] Light and dark themes both meet WCAG AA contrast for text and interactive elements
- [ ] Keyboard focus is visible on every interactive element
- [ ] Base components have unit tests covering their variants and slots

---

### T-202 · Application shell · M · deps: T-201

**Scope:** router with lazy-loaded routes and scroll behaviour, `AppHeader` with responsive
navigation, `AppFooter`, skip-to-content link, theme toggle persisted to `localStorage` and
honouring `prefers-color-scheme`, 404 view, global error boundary.

**Acceptance criteria**
- [ ] All routes are code-split (verified in the build output)
- [ ] Mobile navigation is operable by keyboard and closes on Escape and on route change
- [ ] Theme choice survives a reload; no flash of the wrong theme on first paint
- [ ] An unknown URL renders the 404 view without a console error

---

### T-203 · Typed API client and data composables · M · deps: T-202

**Scope:** `lib/api.ts` (typed `fetch` wrapper, 5 s timeout via `AbortSignal`, problem+json
parsing into `ApiError`, no throwing on expected 404s), `types/` mirroring the API,
`useProjects` / `useProject` / `useProfile` composables with `idle | loading | success |
error` state, and the build-time fallback snapshot from ARCHITECTURE § 6.4.

**Acceptance criteria**
- [ ] Network failure surfaces a typed `ApiError`, never an unhandled rejection
- [ ] When the API is unreachable, the fallback snapshot renders and a notice is shown
- [ ] Requests abort on component unmount (no state updates after unmount)
- [ ] `lib/` reaches 100 % unit coverage with a mocked `fetch`

---

### T-204 · Home page · M · deps: T-203

**Scope:** hero (name, role, one-line value proposition, primary CTA), featured projects,
skills summary, contact CTA, loading skeletons and error state.

**Acceptance criteria**
- [ ] Renders correctly with 0, 1 and many featured projects
- [ ] No layout shift while data loads (skeletons reserve the final dimensions)
- [ ] Page `<head>` sets title, description, canonical and OG tags

---

### T-205 · Projects index · M · deps: T-203 · ∥ T-204

**Scope:** responsive grid of project cards, filter by tag (reflected in the query string),
empty / loading / error states.

**Acceptance criteria**
- [ ] Filter state survives reload and back-navigation via the URL
- [ ] Empty result shows a helpful message with a reset action, not a blank area
- [ ] Cards are fully keyboard-navigable with one clear focus target each

---

### T-206 · Project detail · L · deps: T-203 · ∥ T-204, T-205

**Scope:** case-study layout (context, role, stack, impact metrics), sanitised Markdown body,
mockup gallery with an accessible lightbox, link buttons (live / repo / case study / video),
previous-next navigation, 404 for unknown slugs.

**Acceptance criteria**
- [ ] A project with no links and no mockups renders cleanly (no empty sections)
- [ ] Lightbox traps focus, closes on Escape, and restores focus to the trigger
- [ ] Images declare width and height; the gallery causes no layout shift
- [ ] Unknown slug renders the 404 view

---

### T-207 · About page · M · deps: T-203 · ∥ T-204, T-205, T-206

**Scope:** long-form bio, experience timeline (NICE, Playvox, Easynet, Anglus), education,
skills grouped by category, CV download.

**Acceptance criteria**
- [ ] Timeline is semantic markup (an ordered list), not divs, and reads correctly aloud
- [ ] Overlapping employment periods are presented without implying an error
- [ ] CV link downloads the PDF and is tracked as an outbound link

---

### T-208 · Contact page and form · M · deps: T-203

**Scope:** accessible form (labels, `aria-describedby` errors, `aria-live` status), client-
side validation mirroring the API rules, honeypot, submit states, success and failure
messaging including the 429 case, plus direct email and LinkedIn links as a fallback.

**Acceptance criteria**
- [ ] Errors are announced to screen readers and focus moves to the first invalid field
- [ ] Double-submit is impossible (button disabled while in flight)
- [ ] A 429 response shows a human message using `Retry-After`, not a raw error
- [ ] The form is fully usable with the keyboard alone

---

### T-209 · SEO, meta and PWA basics · M · deps: T-204..T-208

**Scope:** per-route `useHead`, static OG image, `sitemap.xml` and `robots.txt` generated at
build, favicons and `site.webmanifest`, JSON-LD `Person` schema, canonical URLs.

**Acceptance criteria**
- [ ] Every route has a unique title and meta description
- [ ] `sitemap.xml` lists all routes including one entry per project
- [ ] JSON-LD validates against the Schema.org Person type
- [ ] Lighthouse SEO score is 100

---

### T-210 · Image pipeline · M · deps: T-201 · ∥ T-204..T-208

**Scope:** build-time generation of AVIF/WebP responsive variants, a `ResponsiveImage`
component wrapping `<picture>` with `srcset`, `sizes`, `loading="lazy"`,
`decoding="async"` and explicit dimensions; blur-up placeholder for hero images.

**Acceptance criteria**
- [ ] Source PNG/JPG files are never shipped to the browser when AVIF is supported
- [ ] Every image has meaningful `alt` text (decorative images use `alt=""`)
- [ ] CLS stays at or below 0.05 on the projects and detail pages

---

## 7. Epic 3 — Content

### T-301 · Content schema and authoring guide · S · deps: T-001

**Scope:** `content/README.md` explaining the frontmatter schema field by field,
`content/projects/_template.md`, and a worked example project.

**Acceptance criteria**
- [ ] Every field is documented with its type, whether it is required, and an example
- [ ] The guide states how to add a project end to end, including images
- [ ] The template passes `seed --check`

---

### T-302 · Profile content · S · deps: T-301

**Scope:** `content/profile.yml` — bio, experience from the CV (NICE 2024→present, Playvox
2020–2024, Easynet 2017–2020, Anglus 2014–2018), education (Universidad de Caldas,
Systems and Computing Engineering, 2008–2014), skills, languages, links.

**Acceptance criteria**
- [ ] Dates and employers match the CV exactly
- [ ] Bio is written in first person, in English, and is under 120 words
- [ ] Skills reflect current reality, ordered by depth rather than alphabetically

---

### T-303 · Project case studies · L · deps: T-301 · **needs author input**

**Scope:** one `content/projects/<slug>.md` per project, each following the structure
context → role → constraints → what was built → impact, with tags, links and metrics.

**Acceptance criteria**
- [ ] At least 4 projects published, at least 2 with a live or repository link
- [ ] Every project states the author's specific contribution, not the team's
- [ ] Every summary is under 200 characters and works as a standalone card
- [ ] No confidential employer information (verified against NDA constraints)

---

### T-304 · Mockups and imagery · M · deps: T-303 · ∥ T-305

**Scope:** at least one image per project (screenshot, mockup or diagram), consistent
framing, compression, and alt text; portrait photo; OG image.

**Acceptance criteria**
- [ ] Every published project has at least one image with descriptive alt text
- [ ] Images share a consistent aspect ratio and visual treatment
- [ ] No source image exceeds 500 KB in the repository

---

### T-305 · CV hosting and download · S · deps: T-301

**Scope:** an English CV PDF in `apps/web/public/`, linked from About and Home, with the
LinkedIn export removed from the repository root.

**Acceptance criteria**
- [ ] The PDF is under 1 MB and opens in a new tab
- [ ] The filename is professional (`Andres-Medina-CV.pdf`, not `CV Medina Linkedin.pdf`)
- [ ] No personal address or phone number appears in the published file

---

## 8. Epic 4 — Deployment

### T-401 · API container image · M · deps: T-101

**Scope:** multi-stage Dockerfile (uv build stage → slim runtime), non-root user, healthcheck,
`.dockerignore`, `infra/fly.api.toml` with autostop/autostart and a health check.

**Acceptance criteria**
- [ ] Image builds reproducibly and is under 250 MB
- [ ] Container runs as a non-root user (verified with `whoami` in the running container)
- [ ] `docker run` serves `/healthz` locally

---

### T-402 · MongoDB on Fly.io · M · deps: T-401

**Scope:** Fly app with a 1 GB volume, authentication enabled, no public IP, a least-
privilege application user, connection string stored as a Fly secret, and a documented
restore procedure.

**Acceptance criteria**
- [ ] Mongo is unreachable from the public internet (verified from outside Fly)
- [ ] The API connects over the private network and `/readyz` returns 200 in production
- [ ] `docs/RUNBOOK.md` documents backup and restore, tested once end to end

---

### T-403 · Vercel project configuration · S · deps: T-002

**Scope:** Vercel project linked to the repository, SPA rewrite to `index.html`, security
headers (CSP, HSTS, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`),
`VITE_API_BASE_URL` per environment, preview deployments on PRs.

**Acceptance criteria**
- [ ] Deep links such as `/projects/foo` resolve after a hard refresh
- [ ] securityheaders.com grades the site A or better
- [ ] The CSP allows the API origin and blocks inline scripts

---

### T-404 · Deployment workflows · M · deps: T-402, T-403

**Scope:** `deploy-api.yml` (flyctl deploy on merge to main, path-filtered), content seed step
after a successful API deploy, `deploy-web.yml` (Vercel production build with the fallback
snapshot refreshed), and a scheduled `mongodump` backup workflow.

**Acceptance criteria**
- [ ] Merging to `main` deploys both apps without manual steps
- [ ] The seed step runs only after the API reports healthy
- [ ] A failed deploy leaves the previous version serving traffic
- [ ] The backup workflow produces a restorable dump (verified once)

---

### T-405 · Post-deploy smoke tests and uptime monitoring · S · deps: T-404

**Scope:** a post-deploy job asserting `/healthz`, `/readyz`, a projects response and the
home page HTML; an external uptime monitor on `/readyz` with email alerts.

**Acceptance criteria**
- [ ] A broken deploy fails the workflow visibly rather than silently serving errors
- [ ] Downtime triggers an email within 10 minutes (verified by pausing the app once)

---

### T-406 · Custom domain · S · deps: T-405 · *optional, deferred*

**Scope:** purchase a domain, point DNS at Vercel, add the API subdomain, update CORS,
canonical URLs and the sitemap base.

**Acceptance criteria**
- [ ] HTTPS works on the apex and `www`, with one redirecting to the other
- [ ] No mixed-content or CORS errors after the switch

---

## 9. Epic 5 — Quality and launch

### T-501 · End-to-end suite and accessibility · M · deps: T-204..T-208

**Scope:** Playwright specs for home → project → contact, filtering, theme toggle, 404, and
the API-down fallback path; axe-core assertions on every page; mobile viewport run.

**Acceptance criteria**
- [ ] Zero critical or serious axe violations on any page
- [ ] The contact flow is tested against a stubbed API for both success and 429
- [ ] The suite runs in CI in under 3 minutes and is not flaky over 3 consecutive runs

---

### T-502 · Performance budgets · S · deps: T-501

**Scope:** Lighthouse CI with the assertions from ARCHITECTURE § 12, and a bundle-size gate.

**Acceptance criteria**
- [ ] Budgets are enforced in CI and fail a PR that exceeds them
- [ ] Current scores are recorded in PROGRESS.md as the baseline

---

### T-503 · Prerendering (SEO escape hatch) · M · deps: T-209 · *optional*

**Scope:** add `vite-ssg` prerendering for the home page, projects index and every project
detail route, so social crawlers receive real HTML.

**Acceptance criteria**
- [ ] `curl` of a project URL returns its title and description in the HTML source
- [ ] The LinkedIn post inspector shows the project's own preview card

---

### T-504 · Privacy-friendly analytics · S · deps: T-403 · *optional*

**Scope:** cookieless analytics (Vercel Analytics or a self-hosted Umami), page views and
outbound link clicks only.

**Acceptance criteria**
- [ ] No cookies and no consent banner required
- [ ] Analytics failing to load never blocks rendering

---

### T-505 · Security hardening verification · S · deps: T-404

**Scope:** verify every control in ARCHITECTURE § 9, add gitleaks to CI, enable Dependabot
alerts, and run `/security-review` on the full codebase.

**Acceptance criteria**
- [ ] gitleaks reports no findings on full history
- [ ] Rate limiting and the honeypot are verified against the deployed API
- [ ] No high or critical dependency advisories are open

---

### T-506 · Launch · S · deps: all non-optional tickets

**Scope:** final content proofread, cross-browser and real-device check, README badges,
repository description and topics, LinkedIn and GitHub profile updated with the URL.

**Acceptance criteria**
- [ ] Every page proofread by a second reader
- [ ] Verified on iOS Safari and Android Chrome on real devices
- [ ] The public URL is live and linked from LinkedIn and the GitHub profile

---

## 10. Ticket index

| ID | Title | Epic | Size | Depends on | Parallel with |
|---|---|---|---|---|---|
| T-001 | Repository bootstrap and documentation | E0 | S | — | — |
| T-002 | Web application scaffold and tooling | E0 | M | T-001 | T-003, T-005, T-301 |
| T-003 | API application scaffold and tooling | E0 | M | T-001 | T-002, T-005, T-301 |
| T-004 | CI pipeline | E0 | M | T-002, T-003 | T-101, T-201 |
| T-005 | Local development environment | E0 | S | T-001 | T-002, T-003 |
| T-101 | Configuration, logging and error contract | E1 | M | T-003 | T-004, T-201 |
| T-102 | MongoDB connection, models and indexes | E1 | M | T-101 | T-202 |
| T-103 | Projects API | E1 | M | T-102 | T-105, T-107 |
| T-104 | Profile API | E1 | S | T-102, T-107 | T-106 |
| T-105 | Contact API | E1 | M | T-102 | T-103, T-107 |
| T-106 | Email notification via Resend | E1 | S | T-105 | T-104 |
| T-107 | Content seed command | E1 | M | T-102 | T-103, T-105 |
| T-108 | OpenAPI contract snapshot test | E1 | S | T-103, T-105 | T-209 |
| T-201 | Design system and tokens | E2 | M | T-002 | T-004, T-101 |
| T-202 | Application shell | E2 | M | T-201 | T-102 |
| T-203 | Typed API client and data composables | E2 | M | T-202 | T-103, T-107 |
| T-204 | Home page | E2 | M | T-203 | T-205, T-206, T-207, T-208 |
| T-205 | Projects index | E2 | M | T-203 | T-204, T-206, T-207, T-208 |
| T-206 | Project detail | E2 | L | T-203 | T-204, T-205, T-207, T-208 |
| T-207 | About page | E2 | M | T-203 | T-204, T-205, T-206, T-208 |
| T-208 | Contact page and form | E2 | M | T-203 | T-204..T-207 |
| T-209 | SEO, meta and PWA basics | E2 | M | T-204..T-208 | T-210 |
| T-210 | Image pipeline | E2 | M | T-201 | T-204..T-208 |
| T-301 | Content schema and authoring guide | E3 | S | T-001 | T-002, T-003 |
| T-302 | Profile content | E3 | S | T-301 | T-303 |
| T-303 | Project case studies | E3 | L | T-301 | T-302, T-401 |
| T-304 | Mockups and imagery | E3 | M | T-303 | T-305 |
| T-305 | CV hosting and download | E3 | S | T-301 | T-304 |
| T-401 | API container image | E4 | M | T-101 | T-203, T-303 |
| T-402 | MongoDB on Fly.io | E4 | M | T-401 | T-204..T-208 |
| T-403 | Vercel project configuration | E4 | S | T-002 | T-402 |
| T-404 | Deployment workflows | E4 | M | T-402, T-403 | T-209 |
| T-405 | Smoke tests and uptime monitoring | E4 | S | T-404 | T-501 |
| T-406 | Custom domain *(optional)* | E4 | S | T-405 | — |
| T-501 | End-to-end suite and accessibility | E5 | M | T-204..T-208 | T-405 |
| T-502 | Performance budgets | E5 | S | T-501 | T-505 |
| T-503 | Prerendering *(optional)* | E5 | M | T-209 | T-504 |
| T-504 | Privacy-friendly analytics *(optional)* | E5 | S | T-403 | T-503 |
| T-505 | Security hardening verification | E5 | S | T-404 | T-502 |
| T-506 | Launch | E5 | S | all required | — |

**Totals:** 40 tickets — 15 S, 23 M, 2 L. Three are optional (T-406, T-503, T-504); T-303 is
required but blocked on author input.
