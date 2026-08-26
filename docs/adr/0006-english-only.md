# ADR-0006 — English-only for v1

- Status: Accepted
- Date: 2026-08-26

## Context

The author is a native Spanish speaker in Colombia with full professional English, targeting
remote and international roles. Bilingual content doubles the writing and review effort for
every project case study.

## Decision

Ship v1 in English only. No `vue-i18n`, no locale routes, no language switcher.

## Consequences

- One copy of every string; content tickets stay half the size.
- Matches the language of the audience being optimised for (international recruiters).
- **Accepted cost:** Spanish-speaking visitors read English. Given the target audience, an
  acceptable trade.
- Reversibility: user-facing strings live in components rather than in a translation layer,
  so adding `vue-i18n` later means extracting strings — a mechanical, mid-sized refactor.
  If bilingual support becomes likely, do it before the component count grows.
