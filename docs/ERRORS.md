# API error reference

Every non-2xx response from the Portfolio API is `application/problem+json`
([RFC 9457](https://www.rfc-editor.org/rfc/rfc9457), [ADR-0005](./adr/0005-error-contract.md)).
The `type` field of each response links to the section below.

```json
{
  "type": "https://github.com/ThePawn8/personal-portfolio/blob/main/docs/ERRORS.md#validation-error",
  "title": "Validation error",
  "status": 422,
  "detail": "email: value is not a valid email address",
  "instance": "/api/v1/contact",
  "request_id": "01JC4Z8K7Q3M9XKQ0F8W2E5T1V"
}
```

`request_id` is also returned in the `X-Request-ID` header and matches the server log line
for that request. Quote it in any bug report — it is the fastest way to find what happened.

---

## validation-error

**422** · The request body or query parameters did not pass validation.

`detail` lists the offending fields as `field: message`, semicolon-separated, so a form can
show each message next to the input that caused it.

**Fix:** correct the named fields. The full field rules are in `/docs` (OpenAPI).

## project-not-found

**404** · No *published* project exists with the requested slug.

An unpublished project is indistinguishable from a non-existent one by design — draft work
should not be discoverable by guessing URLs.

**Fix:** check the slug against `GET /api/v1/projects`.

## profile-not-found

**404** · Profile content has not been seeded into the database.

**Fix:** run `npm run seed`. In production this means the seed step of the deployment
workflow failed — check the run logs.

## rate-limit-exceeded

**429** · Too many requests from this client for this endpoint.

The `Retry-After` header gives the number of seconds to wait. The contact endpoint allows
5 submissions per hour per client.

**Fix:** wait for the interval in `Retry-After`. If a legitimate user hits this, the limit
is in `CONTACT_RATE_LIMIT_PER_HOUR`.

## dependency-unavailable

**503** · A dependency the endpoint requires — currently only MongoDB — is unreachable.

Returned by `/readyz` when the database does not answer. `/healthz` deliberately keeps
returning 200 in this situation: the process is alive, and restarting it would not help.

**Fix:** check database connectivity. The site keeps serving its build-time content
snapshot while this lasts.

## not-found

**404** · No route matches the requested path.

**Fix:** check the path against `/openapi.json`.

## method-not-allowed

**405** · The route exists but does not accept this HTTP method.

## bad-request

**400** · The request was malformed in a way that validation could not describe more
precisely — usually an unparseable body.

## unauthorized · forbidden

**401 / 403** · Reserved. The public API has no authenticated endpoints today; these exist
so that adding one cannot invent a new error shape.

## internal-error

**500** · An unhandled exception.

The response deliberately contains no internals: a stack trace in a response body is an
information leak and is useless to the caller. The full traceback is logged against the
same `request_id` shown in the response.

**Fix:** report it with the `request_id`.
