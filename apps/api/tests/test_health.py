"""Health endpoint behaviour."""

from httpx import AsyncClient

from portfolio_api import __version__


async def test_healthz_reports_ok(client: AsyncClient) -> None:
    response = await client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": __version__}


async def test_healthz_does_not_depend_on_the_database(client: AsyncClient) -> None:
    """Liveness must stay green while dependencies are down.

    If this probe ever pings MongoDB, a database outage turns into a restart loop that
    takes the API down with it. The assertion here is deliberately about speed and
    isolation rather than payload.
    """
    response = await client.get("/healthz")

    assert response.status_code == 200
    assert response.elapsed.total_seconds() < 1


async def test_openapi_schema_is_served(client: AsyncClient) -> None:
    response = await client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "Portfolio API"
    assert "/healthz" in schema["paths"]


async def test_openapi_documents_the_error_contract(client: AsyncClient) -> None:
    """A client should learn the error shape from the contract, not from a failed request."""
    schema = (await client.get("/openapi.json")).json()

    responses = schema["paths"]["/healthz"]["get"]["responses"]
    assert {"404", "422", "429", "500"} <= responses.keys()
    assert "Problem" in schema["components"]["schemas"]

    problem_properties = schema["components"]["schemas"]["Problem"]["properties"]
    assert {"type", "title", "status", "detail", "instance", "requestId"} <= (
        problem_properties.keys()
    )
