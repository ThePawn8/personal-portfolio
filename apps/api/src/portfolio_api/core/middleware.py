"""Request-scoped context and access logging."""

import re
import time

import structlog
from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send
from ulid import ULID

from portfolio_api.core.logging import get_logger, request_id_var

logger = get_logger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"

# An inbound id is echoed so a caller can correlate across systems, but it is untrusted
# input that ends up in log files: constrain it rather than logging whatever arrives.
_SAFE_REQUEST_ID = re.compile(r"^[A-Za-z0-9._-]{8,64}$")


class RequestContextMiddleware:
    """Assign a request id, expose it, and log one line per request.

    The id is a ULID: like a UUID it is unique without coordination, and unlike a UUID it
    sorts chronologically, so log lines and ids stay in agreement.

    Written as raw ASGI rather than `BaseHTTPMiddleware` deliberately. `BaseHTTPMiddleware`
    runs the downstream application in a separate task, and in Starlette 1.6 that severs the
    context the route-level exception handling depends on — validation errors stop reaching
    their handler and surface as 500s. Raw ASGI keeps one task, one context.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        incoming = Headers(scope=scope).get(REQUEST_ID_HEADER)
        request_id = incoming if incoming and _SAFE_REQUEST_ID.match(incoming) else str(ULID())

        request_id_var.set(request_id)
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        started = time.perf_counter()
        status_code = 500

        async def send_with_request_id(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
                MutableHeaders(raw=message["headers"])[REQUEST_ID_HEADER] = request_id
            await send(message)

        try:
            await self.app(scope, receive, send_with_request_id)
        except Exception:
            # Logged here with timing, then re-raised so the error handler still owns the
            # response shape. `logger.exception` records the traceback.
            logger.exception(
                "request_failed",
                method=scope["method"],
                path=scope["path"],
                duration_ms=round((time.perf_counter() - started) * 1000, 2),
            )
            raise

        logger.info(
            "request_completed",
            method=scope["method"],
            path=scope["path"],
            status_code=status_code,
            duration_ms=round((time.perf_counter() - started) * 1000, 2),
        )
