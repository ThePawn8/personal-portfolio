"""Application factory and ASGI entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from portfolio_api import __version__
from portfolio_api.core.config import Settings, get_settings
from portfolio_api.core.errors import register_exception_handlers
from portfolio_api.core.logging import configure_logging, get_logger
from portfolio_api.core.middleware import REQUEST_ID_HEADER, RequestContextMiddleware
from portfolio_api.routers import health
from portfolio_api.schemas.problem import Problem

logger = get_logger(__name__)

# Documented on every path operation so the generated contract tells a client what errors
# look like, instead of leaving them to find out from a failing request.
PROBLEM_RESPONSES: dict[int | str, dict[str, object]] = {
    404: {"model": Problem, "description": "Not found (application/problem+json)"},
    422: {"model": Problem, "description": "Validation error (application/problem+json)"},
    429: {"model": Problem, "description": "Rate limit exceeded (application/problem+json)"},
    500: {"model": Problem, "description": "Internal error (application/problem+json)"},
}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage resources whose lifetime matches the application.

    The MongoDB client and Beanie initialisation are wired in here in T-102; the hook
    exists now so nothing has to be restructured when they arrive.
    """
    settings: Settings = app.state.settings
    logger.info("application_started", env=settings.app_env, version=__version__)
    yield
    logger.info("application_stopped")


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build a fully configured application.

    A factory rather than a module-level singleton: tests build an isolated instance per
    case with overridden settings, and no configuration is read at import time.
    """
    settings = settings or get_settings()

    # Human-readable locally, JSON everywhere it will be read by a machine.
    configure_logging(level=settings.log_level, json_output=settings.app_env != "local")

    app = FastAPI(
        title="Portfolio API",
        version=__version__,
        summary="Serves portfolio project content and receives contact messages.",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url=None,
        openapi_url="/openapi.json",
        responses=PROBLEM_RESPONSES,
    )
    app.state.settings = settings

    # Middleware added last runs first. CORS is outermost so that error responses — which
    # are produced deeper in the stack — still carry the headers a browser needs to read
    # them; without that, a 429 reaches the UI as an opaque network failure.
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        # No cookies or Authorization headers are used, so credentials stay off. This is
        # also what makes the exact-origin allowlist safe to reason about.
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", REQUEST_ID_HEADER],
        expose_headers=[REQUEST_ID_HEADER, "Retry-After"],
        max_age=600,
    )

    register_exception_handlers(app)

    app.include_router(health.router)

    return app


app = create_app()
