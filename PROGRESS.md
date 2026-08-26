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
| **Phase** | Wave 1 in progress |
| **Next ticket** | T-003 · API scaffold (T-005, T-301 can run in parallel) |
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
| uv | not installed | needed for T-003 → `pip install uv` |
| Docker | not installed | needed for local Mongo (T-005) → Docker Desktop |
| make | not installed | use the npm equivalents (`npm run check`, `npm run dev`, …) |

```bash
make db-up     # MongoDB via docker compose
make dev       # API :8000 + web :5173
make check     # lint + typecheck + tests, both apps
make seed      # load content/ into MongoDB
```

**Known gap:** the GitHub token lacks the `workflow` scope, so pushing `.github/workflows/`
will be rejected. Fix once with `gh auth refresh -h github.com -s workflow`.

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
| T-003 | API application scaffold and tooling | ⬜ | — | Needs `pip install uv` first |
| T-005 | Local development environment | ⬜ | — | Needs Docker Desktop |
| T-301 | Content schema and authoring guide | ⬜ | — | No dependencies — good parallel starter |

### Wave 2
| ID | Ticket | Status | PR | Notes |
|---|---|---|---|---|
| T-004 | CI pipeline | ⬜ | — | Needs the `workflow` token scope |
| T-101 | Configuration, logging and error contract | ⬜ | — | |
| T-201 | Design system and tokens | ⬜ | — | Needs a visual direction decision |
| T-302 | Profile content | ⬜ | — | Source data extracted from the CV, see § 6 |

### Wave 3
| ID | Ticket | Status | PR | Notes |
|---|---|---|---|---|
| T-102 | MongoDB connection, models and indexes | ⬜ | — | |
| T-202 | Application shell | ⬜ | — | |
| T-303 | Project case studies | ⛔ | — | Blocked: needs the project list from the author |
| T-304 | Mockups and imagery | ⛔ | — | Blocked by T-303 |

### Wave 4
| ID | Ticket | Status | PR | Notes |
|---|---|---|---|---|
| T-103 | Projects API | ⬜ | — | |
| T-105 | Contact API | ⬜ | — | |
| T-107 | Content seed command | ⬜ | — | |
| T-203 | Typed API client and data composables | ⬜ | — | |
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

---

## 8. Session log

Newest first. One entry per working session: what shipped, what was learned, what is next.

### 2026-08-26 — Session 2 · Wave 1

**Shipped**
- **T-002 merged** — web scaffold with every quality gate green: `vue-tsc` strict build,
  ESLint 10 flat config with type-checked rules, Prettier, Vitest (2 tests, 100 % coverage),
  Playwright (4 tests on chromium + Pixel 7 viewport), production build

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
