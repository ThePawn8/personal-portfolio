# ADR-0005 — RFC 9457 problem+json as the single error contract

- Status: Accepted
- Date: 2026-08-26

## Context

FastAPI returns `{"detail": ...}` for HTTP errors and a different, nested shape for
validation errors. A client that wants to display a useful message ends up branching on
response shape.

## Decision

Normalise every non-2xx response to `application/problem+json` (RFC 9457) with `type`,
`title`, `status`, `detail`, `instance` and a `request_id`, via exception handlers
registered in the app factory.

## Consequences

- The frontend has exactly one error-parsing path (`lib/api.ts` produces a typed `ApiError`).
- Every error a visitor sees carries a `request_id` that matches a log line, so "it failed"
  becomes a searchable incident.
- Domain exceptions (`RateLimitExceeded`, `ProjectNotFound`) map to status codes in one
  place, so routers never build error responses by hand.
- **Accepted cost:** a small amount of handler wiring, and the OpenAPI error schemas must be
  declared explicitly to stay accurate.
