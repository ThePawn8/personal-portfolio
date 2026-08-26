"""Domain exceptions and the RFC 9457 error contract (ADR-0005).

Routers raise domain exceptions; this module is the only place that decides what an error
looks like on the wire. That keeps status codes consistent and stops error payloads from
being reinvented endpoint by endpoint.
"""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from portfolio_api.core.logging import get_logger, request_id_var

logger = get_logger(__name__)

PROBLEM_CONTENT_TYPE = "application/problem+json"

# `type` must be a stable, dereferenceable URI. Pointing it at the error reference in this
# repository means a client developer who follows the link lands on an actual explanation.
PROBLEM_TYPE_BASE = "https://github.com/ThePawn8/personal-portfolio/blob/main/docs/ERRORS.md#"


class AppError(Exception):
    """Base class for expected, domain-level failures.

    Anything raised as an `AppError` is a situation the API anticipated. Everything else
    reaching the handlers is a bug, and is reported as an opaque 500 while the details go
    to the logs.
    """

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    slug: str = "internal-error"
    title: str = "Internal server error"
    default_detail: str = "The request could not be completed."

    def __init__(self, detail: str | None = None, *, headers: dict[str, str] | None = None) -> None:
        self.detail = detail or self.default_detail
        self.headers = headers or {}
        super().__init__(self.detail)


class ProjectNotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    slug = "project-not-found"
    title = "Project not found"
    default_detail = "No published project exists with that slug."


class ProfileNotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    slug = "profile-not-found"
    title = "Profile not found"
    default_detail = "Profile content has not been seeded."


class RateLimitExceededError(AppError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    slug = "rate-limit-exceeded"
    title = "Too many requests"
    default_detail = "Rate limit exceeded. Try again later."

    def __init__(self, *, retry_after_seconds: int) -> None:
        # Retry-After turns "try again later" into something a client can act on, and lets
        # the UI show a real countdown instead of a shrug.
        super().__init__(headers={"Retry-After": str(retry_after_seconds)})
        self.retry_after_seconds = retry_after_seconds


class DependencyUnavailableError(AppError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    slug = "dependency-unavailable"
    title = "Service unavailable"
    default_detail = "A required dependency is unavailable."


def build_problem(
    *,
    request: Request,
    status_code: int,
    slug: str,
    title: str,
    detail: str,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    """Render any failure as the one error shape this API promises."""
    request_id = request_id_var.get()
    payload: dict[str, Any] = {
        "type": f"{PROBLEM_TYPE_BASE}{slug}",
        "title": title,
        "status": status_code,
        "detail": detail,
        "instance": request.url.path,
        "request_id": request_id,
    }

    # Unhandled exceptions are turned into responses by the outermost middleware, which sits
    # outside RequestContextMiddleware — so the header is set here too, or 500s would be the
    # one case where the client cannot read the id from the headers.
    response_headers = {**(headers or {}), "X-Request-ID": request_id}

    return JSONResponse(
        status_code=status_code,
        content=payload,
        media_type=PROBLEM_CONTENT_TYPE,
        headers=response_headers,
    )


_STATUS_TITLES = {
    status.HTTP_400_BAD_REQUEST: ("bad-request", "Bad request"),
    status.HTTP_401_UNAUTHORIZED: ("unauthorized", "Unauthorized"),
    status.HTTP_403_FORBIDDEN: ("forbidden", "Forbidden"),
    status.HTTP_404_NOT_FOUND: ("not-found", "Not found"),
    status.HTTP_405_METHOD_NOT_ALLOWED: ("method-not-allowed", "Method not allowed"),
    status.HTTP_429_TOO_MANY_REQUESTS: ("rate-limit-exceeded", "Too many requests"),
}


async def handle_app_error(request: Request, exc: Exception) -> JSONResponse:
    """Expected domain failures: the exception already knows how it should be reported."""
    assert isinstance(exc, AppError)  # noqa: S101 - registered only for AppError
    return build_problem(
        request=request,
        status_code=exc.status_code,
        slug=exc.slug,
        title=exc.title,
        detail=exc.detail,
        headers=exc.headers,
    )


async def handle_http_exception(request: Request, exc: Exception) -> JSONResponse:
    """Starlette's own 404s and 405s, normalised into the same shape."""
    assert isinstance(exc, StarletteHTTPException)  # noqa: S101 - registered for this type
    slug, title = _STATUS_TITLES.get(exc.status_code, ("error", "Error"))
    detail = str(exc.detail) if exc.detail else title
    headers = dict(exc.headers) if exc.headers else None
    return build_problem(
        request=request,
        status_code=exc.status_code,
        slug=slug,
        title=title,
        detail=detail,
        headers=headers,
    )


async def handle_validation_error(request: Request, exc: Exception) -> JSONResponse:
    """Request validation failures.

    FastAPI's default payload is a nested list that a UI cannot show to a person. This
    flattens it to `field: message`, which a form can render next to the offending input.
    """
    assert isinstance(exc, RequestValidationError)  # noqa: S101 - registered for this type
    problems: list[str] = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error["loc"] if part != "body")
        problems.append(f"{location}: {error['msg']}" if location else error["msg"])

    return build_problem(
        request=request,
        # UNPROCESSABLE_ENTITY is deprecated in Starlette 1.6 in favour of this spelling.
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        slug="validation-error",
        title="Validation error",
        detail="; ".join(problems),
    )


async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    """Anything unanticipated.

    The client gets no internals — a stack trace in a response body is an information leak
    and is useless to them anyway. The full exception goes to the logs under the same
    request id the client is shown, so the two can be joined.
    """
    logger.exception(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
        exc_type=type(exc).__name__,
    )
    return build_problem(
        request=request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        slug="internal-error",
        title="Internal server error",
        detail="The request could not be completed. Quote the request_id when reporting this.",
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Wire every error path to the problem+json contract."""
    app.add_exception_handler(AppError, handle_app_error)
    app.add_exception_handler(StarletteHTTPException, handle_http_exception)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(Exception, handle_unexpected_error)
