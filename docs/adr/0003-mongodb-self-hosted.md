# ADR-0003 — Self-hosted MongoDB on Fly.io

- Status: Accepted
- Date: 2026-08-26

## Context

Project content and contact messages need persistence. MongoDB Atlas offers a free managed
M0 cluster; Fly.io can run a Mongo container on a persistent volume next to the API.

## Decision

Run MongoDB 7 as a Fly app with a 1 GB volume, on the private 6PN network, with
authentication enabled and no public IP.

## Consequences

- API and database sit in the same region on a private network: no egress cost, no TLS
  handshake to a third party, latency in the low single-digit milliseconds.
- **Accepted cost:** a single node is not a replica set, so there are **no multi-document
  transactions** and **no failover**. Acceptable because writes are one independent document
  at a time (a contact message) and reads are content.
- Backups are the author's responsibility: Fly volume snapshots (daily, 5-day retention)
  plus a scheduled `mongodump` (T-404). Recovery of content depends on neither — the source
  of truth for projects is git, and `make seed` rebuilds the database.
- Operational surface: Mongo version upgrades become a manual task.

## Alternatives rejected

- **Atlas M0:** less work and managed backups, but adds a third provider, a public network
  hop, and a free tier that idles.
- **Postgres:** better fit for relational content, but the author chose MongoDB.
