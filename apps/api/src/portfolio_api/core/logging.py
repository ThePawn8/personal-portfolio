"""Structured logging.

Logs are JSON in every deployed environment so they can be filtered and correlated, and
human-readable locally so they can be read. Every line carries the `request_id` of the
request that produced it, which is what turns "it failed for a user" into a single query.
"""

import logging
import sys
from contextvars import ContextVar
from typing import Any

import structlog

# Set by RequestContextMiddleware; read by the log processor below and by error handlers.
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


def add_request_id(
    _logger: Any,
    _method_name: str,
    event_dict: structlog.types.EventDict,
) -> structlog.types.EventDict:
    """Attach the current request id, when there is one.

    Startup and shutdown logs have no request, so the key is omitted rather than emitted
    empty — an always-present key that is sometimes meaningless is worse than an absent one.
    """
    request_id = request_id_var.get()
    if request_id:
        event_dict["request_id"] = request_id
    return event_dict


def configure_logging(*, level: str = "INFO", json_output: bool = True) -> None:
    """Configure structlog and route the standard library through it.

    Uvicorn and any third-party library log through `logging`; without this they would
    bypass the JSON formatting and produce two incompatible log formats in one stream.
    """
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        add_request_id,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    renderer: structlog.types.Processor = (
        structlog.processors.JSONRenderer()
        if json_output
        else structlog.dev.ConsoleRenderer(colors=True)
    )

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelNamesMapping()[level]),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        # Caching bound loggers on first use is a small speed win that breaks anything
        # which reconfigures logging afterwards — including `create_app` per test and
        # structlog's own `capture_logs`. Correctness over a few microseconds per line.
        cache_logger_on_first_use=False,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.getLevelNamesMapping()[level],
        force=True,
    )

    # Uvicorn's own access log duplicates RequestContextMiddleware, without the request id.
    logging.getLogger("uvicorn.access").disabled = True


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a bound logger. Prefer module-level `logger = get_logger(__name__)`."""
    return structlog.get_logger(name)  # type: ignore[no-any-return]
