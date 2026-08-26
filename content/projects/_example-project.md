---
# A filled-in reference showing what "good" looks like. The leading underscore means this
# file is never published, whatever `published` says. Invented product, invented numbers.

slug: agent-workspace-redesign
title: Agent Workspace Redesign
summary:
  Rebuilt a support agent workspace around a virtualised inbox, cutting time-to-first-reply
  by a third for teams handling 2,000+ daily conversations.

kind: professional
role: Frontend Developer
organisation: Example Corp

period:
  start: '2023-03'
  end: '2024-02'

stack: [vue, typescript, pinia, vite, websockets]
tags: [frontend, performance, accessibility, design-system]

published: false
featured: true
order: 10
confidential: true

links:
  live: null # under NDA — the product is behind a login
  repo: null
  case_study: null
  video: null

metrics:
  - label: Time to first reply
    value: '-34%'
  - label: Inbox render, 5k conversations
    value: '3.8 s → 0.6 s'
  - label: Components migrated
    value: '112'

mockups:
  - src: agent-workspace-redesign/architecture.png
    alt:
      Architecture diagram showing the websocket gateway feeding a normalised Pinia store
      that backs a virtualised conversation list.
    caption: Data flow after the redesign — one socket, one store, one source of truth.
    width: 1600
    height: 900
---

## Context

Support agents worked in a single-page inbox that rendered every open conversation at once.
At around 800 conversations it stayed usable; the largest customers ran 5,000, where opening
the inbox froze the tab for several seconds and typing lagged behind the keyboard. Agents
worked around it by keeping six browser tabs open, which multiplied the websocket
connections and made the problem worse.

Rewriting the product was not on the table: the workspace was in use by paying customers
every hour of the day, and the team was three frontend engineers.

## What I built

I replaced the rendering strategy rather than the application. The conversation list became
a virtualised viewport rendering only what fits on screen plus a small overscan, backed by a
normalised Pinia store keyed by conversation id.

The harder half was the socket layer. Each open tab had held its own connection and its own
copy of the state, so the same message could arrive three times and reconcile differently.
I consolidated it into one connection per session with a sequence-numbered event log, and
made reconnection resume from the last acknowledged sequence rather than refetching
everything.

I chose not to introduce a virtualisation library. The list has variable-height rows with
inline expansion, and every candidate library needed enough patching that owning ~200 lines
of well-tested code was the cheaper long-term position.

The migration shipped in six releasable phases behind a per-customer flag, so the product
never froze and any phase could be reverted independently.

## Impact

Time to first reply — the metric the support organisation is measured on — dropped 34 % for
the largest accounts. Initial inbox render went from 3.8 s to 0.6 s at 5,000 conversations,
and memory per tab fell by roughly two thirds. Agents stopped opening multiple tabs, which
removed the duplicate-connection load entirely.

112 components moved to the new store and the design system in the process, and the
accessibility audit that had blocked a public-sector deal came back clean.

## Reflection

I would introduce the sequence-numbered event log first, before the virtualisation work.
Two of the three bugs that reached production came from reconciling optimistic UI updates
against a socket that could still deliver duplicates — a class of bug the log made
impossible once it existed.
