# Progress

> **Read this first when resuming work.** It is the working memory of the project: what is
> done, what is in flight, what is blocked, and what to pick up next. Update it in the same
> PR as the work it describes — a stale progress file is worse than none.
>
> Reading order for a cold start: this file → [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)
> → [docs/IMPLEMENTATION_PLAN.md](./docs/IMPLEMENTATION_PLAN.md) (only the ticket you are
> working on).

---

## 1. Snapshot

| | |
|---|---|
| **Last updated** | 2026-08-26 |
| **Phase** | Waves 1–2 complete; Wave 3 in progress |
| **Next ticket** | T-104 · Profile API + T-302 · Profile content |
| **Web URL** | not deployed yet |
| **API URL** | not deployed yet |
| **GitHub** | [ThePawn8/personal-portfolio](https://github.com/ThePawn8/personal-portfolio) — public |
| **Blocked on** | Author input for T-303 (project case studies) — see § 5 |

---

## 2. Environment quickstart

Verified on this machine (Windows 11, Git Bash):

| Tool | Version | Notes |
|---|---|---|
| Node | 24.18.0 | `.nvmrc` pins 24 |
| npm | 11.16.0 | pnpm not installed; npm is the package manager |
| Python | 3.12.10 | |
| git | 2.55.0 | |
| gh | 2.96.0 | authenticated as `ThePawn8` |
| uv | 0.12.6 | installed in session 2; `apps/api/uv.lock` is committed |
| Docker | not installed | **not required**: local MongoDB runs via `mongodb-memory-server` (recipe in README) |
| make | not installed | use the npm equivalents (`npm run check`, `npm run dev`, …) |

```bash
make db-up     # MongoDB via docker compose
make dev       # API :8000 + web :5173
make check     # lint + typecheck + tests, both apps
make seed      # load content/ into MongoDB
```

**Resolved:** pushing `.github/workflows/` turned out to work with the existing `repo`
scope — the `workflow` scope was not needed after all.

---

## 3. Locked decisions

Do not relitigate these without writing an ADR. Full reasoning in
[docs/ARCHITECTURE.md § 14](./docs/ARCHITECTURE.md#14-architecture-decision-records).

| Decision | Choice |
|---|---|
| Frontend | Vue 3 + Vite SPA, TypeScript strict |
| Styling | Tailwind v4 with semantic design tokens |
| Theme | Dark **and** light, both first-class, user toggle persisted, no "secondary" theme |
| Language | English only (v1) |
| Backend | FastAPI, async, Beanie ODM |
| Database | MongoDB 7, self-hosted on Fly.io, private network |
| Content | Markdown + YAML in git, idempotent seed into Mongo |
| Wire format | camelCase JSON, including the problem+json `requestId` — the API maps from its snake_case documents |
| Contact | Persist to Mongo + notify via Resend, rate-limited, honeypot |
| Hosting | Vercel (web) + Fly.io (API + Mongo) |
| Domain | `*.vercel.app` for now; custom domain deferred to T-406 |
| Quality gates | lint + types + unit + integration + e2e + coverage + audit, all blocking |
| Workflow | One ticket → one branch → one PR → squash merge |

---

## 4. Ticket board

Legend: ⬜ todo · 🟨 in progress · ✅ done · ⛔ blocked · ⏭️ deferred

### Wave 0 — bootstrap
| ID | Ticket | Status | PR | Notes |
|---|---|---|---|---|
| T-001 | Repository bootstrap and documentation | ✅ | [#1](https://github.com/ThePawn8/personal-portfolio/pull/1) | Repo created, `main` protected, squash-only merges |

### Wave 1 — scaffolds (parallel)
| ID | Ticket | Status | PR | Notes |
|---|---|---|---|---|
| T-002 | Web application scaffold and tooling | ✅ | [#3](https://github.com/ThePawn8/personal-portfolio/pull/3) | All gates green; baseline bundle 24.07 kB gzip JS, 2.51 kB gzip CSS |
| T-003 | API application scaffold and tooling | ✅ | [#4](https://github.com/ThePawn8/personal-portfolio/pull/4) | ruff + mypy strict + pytest green, 100 % coverage |
| T-005 | Local development environment | ✅ | [#5](https://github.com/ThePawn8/personal-portfolio/pull/5) | ⚠️ Container start-up **not** verified — Docker is not installed here (see § 5, V1) |
| T-301 | Content schema and authoring guide | ✅ | [#6](https://github.com/ThePawn8/personal-portfolio/pull/6) | Schema is the spec T-107 must implement; machine validation ships there |

### Wave 2
| ID | Ticket | Status | PR | Notes |
|---|---|---|---|---|
| T-004 | CI pipeline | ✅ | [#9](https://github.com/ThePawn8/personal-portfolio/pull/9) | 6 jobs, ~1 min wall clock; `ci` is the required check on `main` |
| T-101 | Configuration, logging and error contract | ✅ | [#7](https://github.com/ThePawn8/personal-portfolio/pull/7) | 29 tests, 100 % coverage; error reference at `docs/ERRORS.md` |
| T-201 | Design system and tokens | ✅ | [#8](https://github.com/ThePawn8/personal-portfolio/pull/8) | OKLCH tokens, both themes, contrast verified in CI by `npm run check:contrast` |
| T-302 | Profile content | ⬜ | — | Source data extracted from the CV, see § 6 |

### Wave 3
| ID | Ticket | Status | PR | Notes |
|---|---|---|---|---|
| T-102 | MongoDB connection, models and indexes | ✅ | [#12](https://github.com/ThePawn8/personal-portfolio/pull/12) | 42 tests against a real MongoDB, 98.85 % coverage |
| T-202 | Application shell | ✅ | [#10](https://github.com/ThePawn8/personal-portfolio/pull/10) | Router, header/footer, 3-state theme toggle, 404, skip link |
| T-303 | Project case studies | ⛔ | — | Blocked: needs the project list from the author |
| T-304 | Mockups and imagery | ⛔ | — | Blocked by T-303 |

### Wave 4
| ID | Ticket | Status | PR | Notes |
|---|---|---|---|---|
| T-103 | Projects API | ✅ | [#13](https://github.com/ThePawn8/personal-portfolio/pull/13) | List + detail, ETag/304, camelCase wire format |
| T-105 | Contact API | ⬜ | — | |
| T-107 | Content seed command | ✅ | [#14](https://github.com/ThePawn8/personal-portfolio/pull/14) | Idempotent, sanitised, `--check` gates content PRs in CI |
| T-203 | Typed API client and data composables | ✅ | [#11](https://github.com/ThePawn8/personal-portfolio/pull/11) | Typed client, one loading state machine, snapshot fallback |
| T-401 | API container image | ⬜ | — | |
| T-402 | MongoDB on Fly.io | ⬜ | — | Needs a Fly.io account |

### Wave 5
| ID | Ticket | Status | PR | Notes |
|---|---|---|---|---|
| T-104 | Profile API | ⬜ | — | |
| T-106 | Email notification via Resend | ⬜ | — | Needs a Resend account + API key |
| T-204 | Home page | ⬜ | — | |
| T-205 | Projects index | ⬜ | — | |
| T-206 | Project detail | ⬜ | — | |
| T-207 | About page | ⬜ | — | |
| T-208 | Contact page and form | ⬜ | — | |
| T-403 | Vercel project configuration | ⬜ | — | Needs a Vercel account |
| T-404 | Deployment workflows | ⬜ | — | |

### Wave 6 — hardening and launch
| ID | Ticket | Status | PR | Notes |
|---|---|---|---|---|
| T-108 | OpenAPI contract snapshot test | ⬜ | — | |
| T-209 | SEO, meta and PWA basics | ⬜ | — | |
| T-210 | Image pipeline | ⬜ | — | |
| T-305 | CV hosting and download | ⬜ | — | Needs an English CV PDF |
| T-405 | Smoke tests and uptime monitoring | ⬜ | — | |
| T-501 | End-to-end suite and accessibility | ⬜ | — | |
| T-502 | Performance budgets | ⬜ | — | |
| T-505 | Security hardening verification | ⬜ | — | |
| T-506 | Launch | ⬜ | — | |
| T-406 | Custom domain | ⏭️ | — | Optional |
| T-503 | Prerendering | ⏭️ | — | Optional — do it if LinkedIn previews matter |
| T-504 | Analytics | ⏭️ | — | Optional |

---

## 5. Open questions and blockers

| # | Question | Blocks | Status |
|---|---|---|---|
| Q1 | Which projects go in the portfolio? Name, employer/personal, dates, stack, your specific contribution, measurable impact | T-303, T-304 | **Open** |
| Q2 | Which projects have public links (live site, repository, store listing)? Which are under NDA and can only be described? | T-303 | **Open** |
| Q3 | Do you have screenshots or mockups for any of them, or should we design placeholder visuals? | T-304 | **Open** |
| Q4 | Full name for the site and the CV filename (the CV shows "Andrés M") | T-302, T-305 | **Open** |
| Q5 | Public GitHub and LinkedIn URLs to display | T-302 | **Open** |
| Q6 | Repository name and visibility | T-001 | ✅ `ThePawn8/personal-portfolio`, public |
| Q7 | Visual direction | T-201 | ✅ Dark and light, both first-class, tokenised |
| Q8 | Accounts to create: Fly.io, Vercel, Resend | T-402, T-403, T-106 | **Open** |
| V1 | `npm run db:up` (docker compose) has still never been executed — Docker is not installed. **No longer blocking:** local MongoDB runs without Docker (README → Without Docker), and CI uses a `mongo:7` service container. Verify the compose path whenever Docker gets installed | — | Downgraded to a nice-to-have |

**Agreed way of working on content (Q1–Q3):** the author does not write the case studies from
scratch. For each project, Claude asks a short set of questions (what was built, stack, role,
impact numbers, public link or NDA), drafts the English case study, and the author corrects
facts and figures before it is merged.

---

## 6. Reference data extracted from the CV

Source: `CV Medina Linkedin.pdf` (LinkedIn export, to be replaced in T-305).

- **Name:** Andrés M · **Location:** Manizales, Caldas, Colombia
- **Current role:** Frontend Developer at **NICE** (June 2024 → present)
- **Playvox** — Frontend Developer (June 2020 → September 2024)
- **Easynet S.A.S** — Frontend Developer (February 2017 → June 2020)
- **Anglus S.A.S** — Development Engineer (March 2014 → November 2018): frontend, backend,
  Android applications, API development
- **Education:** Universidad de Caldas — Systems and Computing Engineering (2008–2014)
- **Skills listed:** Python, Django, HTML5, TypeScript, Vue.js, Git
- **Languages:** Spanish (native), English (full professional)
- **Certifications:** TypeScript Essential Training, Learning TypeScript,
  Curso Profesional de Git y GitHub, Curso Profesional de Vue.js

⚠️ The Anglus (2014–2018) and Easynet (2017–2020) periods overlap. Confirm whether these
were concurrent before publishing the timeline (T-302).

---

## 7. Baselines

Recorded so a regression is visible rather than guessed at. Update when they move.

| Metric | Value | Measured |
|---|---|---|
| Web bundle, initial route | 60.41 kB raw / **24.07 kB gzip** (budget 180 kB) | T-002, empty app |
| Web CSS | 8.97 kB raw / **2.51 kB gzip** (budget 30 kB) | T-002, Tailwind base only |
| Web unit coverage | 100 % statements | T-002 |
| Production build time | ~0.4 s | T-002 |
| E2E suite | 4 tests, 5.8 s, chromium + mobile | T-002 |
| API unit coverage | 100 % statements, 5 tests in 0.1 s | T-003 |
| API `/healthz` latency, local | 3.7 ms | T-003 |
| API tests | 83 tests, 95.8 % coverage, real MongoDB | T-107 |
| Web bundle after design system | **26.45 kB gzip** JS, **4.86 kB gzip** CSS | T-201 |
| Web unit tests | 34 tests, 100 % statements | T-201 |
| Contrast checks | 28 pairings, both themes, all passing | T-201 |
| CI wall time | ~1 min (6 jobs in parallel) | T-004 |
| Web bundle with router + shell | **42.80 kB gzip** JS, 5 lazy route chunks | T-202 |
| Web tests | 71 unit (98 % statements), 21 e2e | T-202 |
| Web tests after the API client | 99 unit (96 % statements), 21 e2e | T-203 |

---

## 8. Session log

Newest first. One entry per working session: what shipped, what was learned, what is next.

### 2026-08-26 — Session 2 · Wave 1

**Shipped**
- **T-002 merged** — web scaffold with every quality gate green: `vue-tsc` strict build,
  ESLint 10 flat config with type-checked rules, Prettier, Vitest (2 tests, 100 % coverage),
  Playwright (4 tests on chromium + Pixel 7 viewport), production build
- **T-003 merged** — API scaffold: uv-locked dependencies, Ruff (16 rule families including
  bandit and async correctness), mypy strict, pytest with a coverage gate and
  `filterwarnings = error`, `/healthz` verified against a live uvicorn process
- **T-005 merged** — local environment: MongoDB compose file with authentication, a
  least-privilege app user matching production, loopback-only port binding, and an
  idempotent `npm run setup` that creates `.env` and generates a random `IP_HASH_SALT`
- **T-301 merged** — content authoring guide with the full field reference for projects and
  profile, a template, a worked example, and guidance on writing case studies that name
  *your* contribution and handle NDA work without leaking internals

- **T-101 merged** — settings that fail fast on a bad production config, structlog JSON
  logging with ULID request correlation, and the full RFC 9457 error contract with a
  published reference at [docs/ERRORS.md](./docs/ERRORS.md)

- **T-201 merged** — design tokens in OKLCH for both themes, five base components, and a
  contrast checker that reads the real token values and fails the build below WCAG
  thresholds

- **T-004 merged** — CI runs every gate on every PR: lint, format, types, contrast, unit
  tests with coverage, build, bundle budget, Playwright, gitleaks over full history, npm
  audit and pip-audit. Verified negatively by pushing a deliberate lint failure: the
  `ci` job failed, `e2e` skipped, and the PR moved to BLOCKED once `ci` became a required
  check. `main` now requires it, with strict (up-to-date) branches.

- **T-202 merged** — application shell: code-split router, sticky header with responsive
  navigation, footer, three-state theme control, 404 view, skip link, and recovery from
  stale chunks after a deploy

- **T-203 merged** — typed API client with one error type, one loading state machine for
  every remote resource, and the build-time snapshot fallback. The wire format was fixed
  as camelCase and the API's problem payload aligned in the same PR (ADR-0001: contract
  and consumer land together)

**Waves 1 and 2 are complete except T-302** (profile content, needs the author's full name
and LinkedIn URL).

**T-203 gotchas**
- Vue's `readonly()` returns `DeepReadonly<T>`, which fights every consumer of a generic
  payload. The composable returns `data` and `error` unwrapped and relies on the declared
  interface for read-only intent. ESLint's `no-unnecessary-type-assertion` and `vue-tsc`
  disagreed on the cast that papered over this — the simplification satisfies both.
- `instanceof Error` is unreliable across realms under jsdom: a `DOMException` created in
  application code failed the check inside a test. Compare by `name` instead.
- A `Response` body can only be read once, so `mockResolvedValue(new Response(...))` breaks
  the second call. Use `mockImplementation` to build a fresh one each time.
- The client adds nothing to the bundle yet (42.80 kB gzip, unchanged) because no view
  imports it — it is tree-shaken until T-204 uses it.

**T-202 gotchas**
- **Binding `:href="undefined"` alongside `:to` breaks RouterLink.** The undefined
  attribute falls through onto the anchor and overrides the href RouterLink computed,
  producing an `<a>` with no href — no link role, invisible to assistive technology. Found
  by an e2e test, not by types. Attributes are now composed per element in `BaseButton`,
  with a regression test.
- Playwright cannot `.check()` an `sr-only` radio (it fails the actionability check).
  Click the label instead, which is what a person does anyway.
- e2e files need their own tsconfig with DOM types: `page.evaluate` callbacks run in the
  browser even though the runner is Node.
- jsdom has no layout, so `window.scrollTo` prints "Not implemented" on every navigation.
  Stubbed in `tests/setup.ts`; real scroll restoration is covered in Playwright.
- `router.resolve()` returns a type whose `name` can be `null`, which does not satisfy
  `scrollBehavior`'s parameter. Navigate and read `router.currentRoute.value` instead.

**T-101 gotchas**
- `filterwarnings = ["error"]` earned its place immediately: `status.HTTP_422_UNPROCESSABLE_ENTITY`
  is deprecated in Starlette 1.6, and the warning was raised *inside* the exception handler,
  turning every 422 into a 500. Use `HTTP_422_UNPROCESSABLE_CONTENT`.
- `structlog.testing.capture_logs()` replaces the **entire** processor chain, so any
  processor under test (`merge_contextvars`, `add_request_id`) must be passed to it
  explicitly — otherwise the assertion is about a pipeline that is not ours.
- `cache_logger_on_first_use=True` breaks both `capture_logs` and any reconfiguration, and
  `create_app` reconfigures logging on every call. Turned off.
- Request context is raw ASGI middleware, not `BaseHTTPMiddleware`: no extra task per
  request, no context copying, and no interference with streaming responses.
- Ruff `N818` requires an `Error` suffix on exception names, so the domain exceptions are
  `ProjectNotFoundError`, `RateLimitExceededError` and friends.
- `tests/` is a package (`__init__.py`) so shared helpers import as `tests.conftest`;
  without it mypy sees the same file under two module names and refuses to continue.

**T-201 gotchas**
- `exactOptionalPropertyTypes` forbids `withDefaults(..., { optionalProp: undefined })` —
  optional props must be omitted entirely. `vue/require-default-prop` disagrees, so that
  rule is off with a comment explaining why.
- Tailwind v4 generates utilities from theme namespaces: `--radius-card` gives
  `rounded-card`, `--text-title` gives `text-title`. Use those, not `rounded-[--radius-card]`.
- `@theme inline` is required for runtime theming: without `inline` the utilities bake in
  the resolved colour and a theme switch does nothing.
- Vitest suites that read source files need `// @vitest-environment node`; under jsdom
  `import.meta.url` is an `http://` URL and cannot be converted to a path.

**Learned / gotchas** (all cost real debugging time — do not rediscover them)
- **TS 6 deprecates `baseUrl`.** Use `paths` alone; it resolves relative to the tsconfig file.
- **`allowArbitraryExtensions` breaks CSS imports.** With it on, TypeScript looks for
  `main.d.css.ts` instead of using the `*.css` wildcard declaration.
- **TS 6 raises TS2882 for side-effect CSS imports** even with `vite/client` types loaded.
  Fixed with an explicit `declare module '*.css'` in `src/vite-env.d.ts`.
- **Type-checked ESLint requires every linted file to be in a tsconfig `include`** —
  `eslint.config.ts` lints itself, so it must be listed in `tsconfig.node.json`.
- **Rollup 4 rejects the object form of `manualChunks`** in Vite 8 typings. Chunking is
  deferred to T-502, where it belongs anyway.
- Playwright runs against `vite preview` of a real production build, not the dev server —
  dev-only behaviour hides deployment bugs.
- **Starlette 1.6 deprecates `TestClient` with `httpx`** (it wants `httpx2`). Rather than
  suppress the warning, the lifespan test uses `asgi-lifespan` + `httpx.AsyncClient`, which
  keeps one HTTP library across the suite. Revisit if Starlette forces `httpx2`.
- **`ASGITransport` does not run the lifespan.** Startup failures are invisible to the
  normal fixtures — hence the explicit lifespan test, which matters from T-102 onward when
  the MongoDB connection is opened there.

**Next**
- T-003 (API scaffold) → then T-005 and T-301, which are independent of it

---

### 2026-08-26 — Session 1 · project kickoff

**Shipped**
- GitHub repository created: `ThePawn8/personal-portfolio`, public, `main` protected
  (pull request required, linear history, no force pushes, squash-only merges, branches
  deleted on merge)
- **T-001 merged** as [PR #1](https://github.com/ThePawn8/personal-portfolio/pull/1)
- Architecture decisions taken with the author across three rounds of questions
- `docs/ARCHITECTURE.md` — full technical design, 14 sections with C4 and data-flow diagrams
- `docs/adr/0001..0006` — six architecture decision records
- `docs/IMPLEMENTATION_PLAN.md` — 40 tickets across 5 epics, dependencies and parallel waves
- `PROGRESS.md` — this file
- Repository hygiene: `.gitignore`, `.editorconfig`, `.gitattributes`, `.nvmrc`

**Done but not yet committed**
- `apps/web` Vite scaffold with dependencies installed (Vue 3.5, Vite 8, TS 6, Tailwind 4.3,
  vue-router 5, Pinia 4, Vitest 4, Playwright, ESLint 10). Belongs to T-002 — it must land on
  its own branch and PR, not on the T-001 commit.

**Learned / gotchas**
- The `gh` token lacks the `workflow` scope; pushing workflow files needs
  `gh auth refresh -h github.com -s workflow`
- Installed dependency majors are newer than most online examples (Vite 8, ESLint 10,
  vue-router 5, Pinia 4, TS 6). Verify APIs against the installed version, not from memory.
- Author dropped `CV Medina Linkedin.pdf` in the repository root — data extracted in § 6; the
  file itself should not be committed as-is (T-305).

**Next**
1. Answer the open questions in § 5 (Q1–Q3 are the real critical path — no content, no
   portfolio)
2. Merge T-001, then start Wave 1 (T-002, T-003, T-005, T-301 in parallel)
