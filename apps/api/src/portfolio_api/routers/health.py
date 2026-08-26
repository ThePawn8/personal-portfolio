"""Liveness and readiness probes.

`/healthz` answers "is the process alive" and must never touch a dependency: a failing
database would otherwise make the platform restart a perfectly healthy container.
`/readyz` answers "can this instance serve traffic" and does check dependencies — it is
added in T-102, together with the MongoDB connection it needs to ping.
"""

from fastapi import APIRouter, status

from portfolio_api import __version__
from portfolio_api.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get(
    "/healthz",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness probe",
    response_description="The process is running.",
)
async def healthz() -> HealthResponse:
    return HealthResponse(status="ok", version=__version__)
