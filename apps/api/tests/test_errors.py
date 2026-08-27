"""The RFC 9457 error contract (ADR-0005).

Every one of these asserts the same promise from a different angle: whatever goes wrong,
the client parses one shape and always gets a correlatable request id.
"""

from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel

from portfolio_api.core.errors import (
    PROBLEM_CONTENT_TYPE,
    ProjectNotFoundError,
    RateLimitExceededError,
)

PROBLEM_FIELDS = {"type", "title", "status", "detail", "instance", "requestId"}


class _Payload(BaseModel):
    email: str
    count: int


@pytest.fixture
def failing_app(app: FastAPI) -> FastAPI:
    """The application plus routes that fail in each way we promise to handle."""

    @app.get("/test/domain-error")
    async def _domain_error() -> None:
        raise ProjectNotFoundError

    @app.get("/test/rate-limited")
    async def _rate_limited() -> None:
        raise RateLimitExceededError(retry_after_seconds=42)

    @app.get("/test/boom")
    async def _boom() -> None:
        message = "database on fire"
        raise RuntimeError(message)

    @app.post("/test/validated")
    async def _validated(payload: _Payload) -> _Payload:
        return payload

    return app


@pytest.fixture
async def failing_client(failing_app: FastAPI) -> AsyncIterator[AsyncClient]:
    """Client that returns the 500 response instead of re-raising.

    Starlette re-raises unhandled exceptions after producing the response so the server
    can log them; without this flag the test would see the exception, not the contract.
    """
    transport = ASGITransport(app=failing_app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client


async def test_unknown_route_returns_problem_json(client: AsyncClient) -> None:
    response = await client.get("/does-not-exist")

    assert response.status_code == 404
    assert response.headers["content-type"].startswith(PROBLEM_CONTENT_TYPE)
    body = response.json()
    assert body.keys() >= PROBLEM_FIELDS
    assert body["status"] == 404
    assert body["instance"] == "/does-not-exist"
    assert body["type"].endswith("#not-found")


async def test_domain_error_maps_to_its_status_and_type(failing_client: AsyncClient) -> None:
    response = await failing_client.get("/test/domain-error")

    body = response.json()
    assert response.status_code == 404
    assert body["type"].endswith("#project-not-found")
    assert body["title"] == "Project not found"
    assert body["detail"] == "No published project exists with that slug."


async def test_rate_limit_sets_retry_after(failing_client: AsyncClient) -> None:
    """A client cannot back off intelligently without this header."""
    response = await failing_client.get("/test/rate-limited")

    assert response.status_code == 429
    assert response.headers["retry-after"] == "42"
    assert response.json()["type"].endswith("#rate-limit-exceeded")


async def test_validation_error_names_the_offending_field(failing_client: AsyncClient) -> None:
    """FastAPI's nested default cannot be shown to a person; this can."""
    response = await failing_client.post("/test/validated", json={"count": "not-a-number"})

    assert response.status_code == 422
    body = response.json()
    assert body["type"].endswith("#validation-error")
    assert "email" in body["detail"]
    assert "count" in body["detail"]


async def test_unhandled_exception_is_opaque(failing_client: AsyncClient) -> None:
    """No internals in the body: a stack trace is an information leak."""
    response = await failing_client.get("/test/boom")

    assert response.status_code == 500
    body = response.json()
    assert body.keys() >= PROBLEM_FIELDS
    assert body["type"].endswith("#internal-error")
    assert "database on fire" not in response.text
    assert "Traceback" not in response.text
    assert "RuntimeError" not in response.text


async def test_every_error_carries_a_correlatable_request_id(failing_client: AsyncClient) -> None:
    """Including the 500 path, which is produced outside the request middleware."""
    for path in ("/does-not-exist", "/test/domain-error", "/test/boom"):
        response = await failing_client.get(path)

        assert response.json()["requestId"], f"missing requestId in body for {path}"
        assert response.headers["x-request-id"] == response.json()["requestId"], path


async def test_cors_headers_are_present_on_error_responses(client: AsyncClient) -> None:
    """Without these a 429 reaches the browser as an opaque network failure."""
    response = await client.get("/does-not-exist", headers={"Origin": "http://localhost:5173"})

    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


async def test_cors_rejects_unlisted_origins(client: AsyncClient) -> None:
    response = await client.get("/healthz", headers={"Origin": "https://evil.example"})

    assert "access-control-allow-origin" not in response.headers
