"""Application factory and lifespan behaviour."""

from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from portfolio_api.main import create_app


async def test_lifespan_starts_and_stops_cleanly() -> None:
    """Entering and leaving the app context must not raise.

    The `client` fixture uses a bare `ASGITransport`, which skips the lifespan entirely, so
    without this test a broken startup hook (a bad MongoDB connection, in T-102) would pass
    the whole suite and only fail in production.
    """
    app = create_app()

    async with LifespanManager(app) as manager:
        transport = ASGITransport(app=manager.app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get("/healthz")

    assert response.status_code == 200


def test_factory_returns_independent_instances() -> None:
    """Each call builds a new app, so test state cannot leak between cases."""
    assert create_app() is not create_app()
