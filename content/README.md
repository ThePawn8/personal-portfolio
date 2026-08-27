# Content authoring guide

Everything the site says about projects and experience lives here, in git. It is reviewed in
pull requests, validated in CI, and loaded into MongoDB by an idempotent seed
([ADR-0004](../docs/adr/0004-content-in-git.md)).

```
content/
├── README.md                   this guide
├── profile.yml                 bio, experience, education, skills  (T-302)
└── projects/
    ├── _template.md            copy this to start a new project
    ├── _example-project.md     a filled-in reference, never published
    └── <slug>.md               one file per project
```

Files starting with `_` are never published, whatever their frontmatter says.

---

## Adding a project, end to end

1. **Copy the template**

   ```bash
   cp content/projects/_template.md content/projects/my-project.md
   ```

   The filename must equal the `slug` — it becomes the URL: `/projects/my-project`.

2. **Fill in the frontmatter** using the field reference below. Required fields are
   required; the seed fails loudly rather than publishing a half-filled card.

3. **Write the body.** Four sections, in this order: Context, What I built, Impact,
   and optionally Reflection. Keep it concrete — see *Writing well* below.

4. **Add images** to `apps/web/src/assets/projects/<slug>/`, then reference them from
   `mockups`. Every image needs `alt`, `width` and `height`; the dimensions are what stop
   the page from shifting while images load.

5. **Validate and preview**

   ```bash
   npm run seed:check   # validates without writing to the database
   npm run seed         # upserts into MongoDB
   npm run dev          # see it on the site
   ```

6. **Open a pull request.** Content changes are reviewed like code.

To retire a project, set `published: false`. **Deleting the file does not remove it** — the
seed is additive and never deletes, so a file removed by accident cannot wipe live content.

---

## Project frontmatter reference

| Field | Type | Required | Notes |
|---|---|---|---|
| `slug` | string | ✅ | kebab-case, unique, matches the filename, becomes the URL |
| `title` | string | ✅ | ≤ 60 characters — it has to fit on a card |
| `summary` | string | ✅ | ≤ 200 characters, one sentence. Used on cards, in search results and in link previews |
| `kind` | enum | ✅ | `professional` · `personal` · `open-source` · `freelance` |
| `role` | string | ✅ | Your role, not the team's: "Frontend Developer", "Tech Lead" |
| `organisation` | string | ➖ | Employer or client. Omit for personal projects |
| `period.start` | `YYYY-MM` | ✅ | |
| `period.end` | `YYYY-MM` or `null` | ✅ | `null` means ongoing |
| `stack` | string[] | ✅ | ≥ 1, lowercase tokens: `vue`, `typescript`, `fastapi`, `mongodb` |
| `tags` | string[] | ✅ | ≥ 1, drives filtering on the projects page: `frontend`, `performance`, `accessibility` |
| `published` | boolean | ✅ | `false` hides it everywhere |
| `featured` | boolean | ➖ | Default `false`. Featured projects appear on the home page |
| `order` | integer | ➖ | Default `100`. Lower sorts first, within featured and non-featured groups |
| `confidential` | boolean | ➖ | Default `false`. `true` documents that internals are deliberately omitted |
| `links.live` | URL | ➖ | Public product or demo |
| `links.repo` | URL | ➖ | Source code |
| `links.case_study` | URL | ➖ | Longer write-up elsewhere |
| `links.video` | URL | ➖ | Demo recording |
| `metrics[].label` | string | ➖ | ≤ 4 entries. What was measured: "Checkout conversion" |
| `metrics[].value` | string | ➖ | The number, as a string: `"+12%"`, `"1.2 s → 0.4 s"` |
| `mockups[].src` | path | ➖ | Relative to `apps/web/src/assets/projects/` |
| `mockups[].alt` | string | ✅ if `src` | What the image *shows*, for someone who cannot see it |
| `mockups[].caption` | string | ➖ | Shown under the image |
| `mockups[].width` | integer | ✅ if `src` | Intrinsic pixel width — required to prevent layout shift |
| `mockups[].height` | integer | ✅ if `src` | Intrinsic pixel height |

**Dates are `YYYY-MM` strings, quoted.** Unquoted `2024-06` is parsed by YAML as a date and
loses its meaning; quoted, it stays exactly what you wrote.

---

## Profile reference (`profile.yml`)

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | ✅ | Displayed name |
| `headline` | string | ✅ | ≤ 80 characters: "Frontend Developer · Vue and TypeScript" |
| `location` | string | ✅ | City, country |
| `bio` | string | ✅ | First person, ≤ 120 words |
| `email` | email | ➖ | Public contact address. Omit it to route everything through the contact form — publishing an address invites spam |
| `links.github` | URL | ✅ | |
| `links.linkedin` | URL | ✅ | |
| `links.cv` | path | ➖ | PDF in `apps/web/public/` |
| `languages[].name` | string | ✅ | |
| `languages[].level` | string | ✅ | "Native", "Full professional" |
| `skills[].group` | string | ✅ | "Frontend", "Backend", "Tooling" |
| `skills[].items` | string[] | ✅ | Ordered by depth, not alphabetically |
| `experience[].company` | string | ✅ | |
| `experience[].role` | string | ✅ | |
| `experience[].start` | `YYYY-MM` | ✅ | |
| `experience[].end` | `YYYY-MM` or `null` | ✅ | `null` means current |
| `experience[].summary` | string | ✅ | One or two sentences |
| `experience[].highlights` | string[] | ➖ | 2–4 bullets, each starting with a verb |
| `education[].institution` | string | ✅ | |
| `education[].degree` | string | ✅ | |
| `education[].start` / `.end` | `YYYY` | ✅ | |
| `certifications[]` | string[] | ➖ | |

---

## Writing well

The difference between a portfolio that gets replies and one that does not is almost never
the design.

**Write what *you* did.** "The team migrated to Vue 3" tells a reader nothing about you.
"I led the Vue 3 migration of 40 components, splitting it into 6 releasable phases so the
product never froze" tells them what you would do for them.

**Use numbers, even approximate ones.** "Improved performance" is noise. "Cut LCP from 4.1 s
to 1.6 s on mobile" is evidence. If you cannot measure the outcome, measure the scope: how
many users, screens, services, engineers.

**State the constraint.** Work is only impressive relative to what made it hard — a
deadline, a legacy system, a two-person team, a browser you had to support.

**Respect confidentiality.** Never publish internal metrics, customer names, screenshots of
private dashboards or unreleased features. Under NDA, describe the *problem shape* and your
*approach*, set `confidential: true`, and replace screenshots with an architecture diagram
you drew yourself. A well-drawn diagram often reads better than a product screenshot anyway.

**Cut the adjectives.** "Robust, scalable, cutting-edge" survive no contact with a reviewer.
Specifics do.

### Body structure

```markdown
## Context
The situation and the problem. Who used it, what was wrong, what was at stake.

## What I built
Your work specifically. Decisions and trade-offs, not a feature list.

## Impact
What changed. Numbers where they exist, scope where they do not.

## Reflection   (optional)
What you would do differently. Judgement is a senior signal — it is not a confession.
```

---

## Validation

`npm run seed:check` validates every file against the schema and exits non-zero on the first
problem, naming the file and the field. CI runs it on every pull request that touches
`content/`, so a malformed project fails the build instead of appearing broken in production.

> The validator itself ships with the seed command in **T-107**. Until then this document is
> the specification, and the schema in the template is the contract T-107 must implement.
