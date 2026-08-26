"""Application factory and ASGI entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from portfolio_api import __version__
from portfolio_api.routers import health


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Manage resources whose lifetime matches the application.

    The MongoDB client and Beanie initialisation are wired in here in T-102; the
    hook exists now so nothing has to be restructured when they arrive.
    """
    yield


def create_app() -> FastAPI:
    """Build a fully configured application.

    A factory rather than a module-level singleton: tests build an isolated instance
    per case, and configuration can be overridden without import-time side effects.
    """
    app = FastAPI(
        title="Portfolio API",
        version=__version__,
        summary="Serves portfolio project content and receives contact messages.",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url=None,
        openapi_url="/openapi.json",
    )

    app.include_router(health.router)

    return app


app = create_app()
