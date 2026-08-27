"""Conditional requests and cache headers.

Portfolio content changes roughly monthly but is requested on every page load. Five minutes
of freshness plus an ETag means a returning visitor usually gets a 304 with an empty body,
and the origin does almost no work — without ever serving content that is more than five
minutes stale.
"""

import hashlib
import json
from typing import Any

from fastapi import Response
from starlette.requests import Request
from starlette.responses import JSONResponse

PUBLIC_CACHE_CONTROL = "public, max-age=300, stale-while-revalidate=600"


def compute_etag(payload: Any) -> str:
    """A strong ETag derived from the response body.

    Content-derived rather than time-derived: two deploys that produce identical content
    keep the same ETag, so a redeploy does not invalidate every visitor's cache.
    """
    serialised = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    digest = hashlib.sha256(serialised.encode()).hexdigest()[:32]
    return f'"{digest}"'


def cached_json_response(request: Request, payload: Any) -> Response:
    """Return the payload, or a 304 when the client already has this exact version."""
    etag = compute_etag(payload)

    # `If-None-Match` may carry several tags, and a proxy may weaken them with the W/ prefix.
    candidates = {
        tag.strip().removeprefix("W/")
        for tag in request.headers.get("if-none-match", "").split(",")
    }

    if etag in candidates:
        return Response(
            status_code=304,
            headers={"ETag": etag, "Cache-Control": PUBLIC_CACHE_CONTROL},
        )

    return JSONResponse(
        content=payload,
        headers={"ETag": etag, "Cache-Control": PUBLIC_CACHE_CONTROL},
    )
