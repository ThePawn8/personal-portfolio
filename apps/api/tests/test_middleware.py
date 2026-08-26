"""Request context: id assignment, propagation and access logging."""

import structlog
from httpx import AsyncClient

from portfolio_api.core.logging import add_request_id
from portfolio_api.core.middleware import REQUEST_ID_HEADER

ULID_LENGTH = 26


async def test_generates_a_request_id_when_none_is_supplied(client: AsyncClient) -> None:
    response = await client.get("/healthz")

    request_id = response.headers[REQUEST_ID_HEADER]
    assert len(request_id) == ULID_LENGTH
    assert request_id.isalnum()


async def test_request_ids_are_unique_per_request(client: AsyncClient) -> None:
    first = await client.get("/healthz")
    second = await client.get("/healthz")

    assert first.headers[REQUEST_ID_HEADER] != second.headers[REQUEST_ID_HEADER]


async def test_request_ids_sort_chronologically(client: AsyncClient) -> None:
    """ULIDs are lexicographically ordered by time, so sorted logs are ordered logs."""
    first = await client.get("/healthz")
    second = await client.get("/healthz")

    assert first.headers[REQUEST_ID_HEADER] < second.headers[REQUEST_ID_HEADER]


async def test_echoes_a_well_formed_inbound_request_id(client: AsyncClient) -> None:
    """Lets a caller correlate this request with its own logs."""
    response = await client.get("/healthz", headers={REQUEST_ID_HEADER: "upstream-trace-0001"})

    assert response.headers[REQUEST_ID_HEADER] == "upstream-trace-0001"


async def test_replaces_a_malformed_inbound_request_id(client: AsyncClient) -> None:
    """The id reaches log files, so unconstrained input is not echoed into them."""
    hostile = "x" * 500 + "\ninjected-log-line"

    response = await client.get("/healthz", headers={REQUEST_ID_HEADER: hostile})

    assert response.headers[REQUEST_ID_HEADER] != hostile
    assert len(response.headers[REQUEST_ID_HEADER]) == ULID_LENGTH


async def test_logs_one_line_per_request_with_correlation(client: AsyncClient) -> None:
    # capture_logs() replaces the whole processor chain, so the two processors under test
    # have to be reinstated — otherwise this would assert on a pipeline that is not ours.
    correlation_processors = [structlog.contextvars.merge_contextvars, add_request_id]

    with structlog.testing.capture_logs(processors=correlation_processors) as captured:
        response = await client.get("/healthz")

    completed = [entry for entry in captured if entry["event"] == "request_completed"]
    assert len(completed) == 1

    entry = completed[0]
    assert entry["method"] == "GET"
    assert entry["path"] == "/healthz"
    assert entry["status_code"] == 200
    assert entry["duration_ms"] >= 0
    assert entry["request_id"] == response.headers[REQUEST_ID_HEADER]
