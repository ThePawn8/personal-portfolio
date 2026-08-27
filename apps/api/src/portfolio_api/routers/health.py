"""Liveness and readiness probes.

`/healthz` answers "is the process alive" and must never touch a dependency: a failing
database would otherwise make the platform restart a perfectly healthy container, turning a
degraded read path into a full outage.

`/readyz` answers "can this instance serve traffic" and does check the database. It is the
probe for humans and for the uptime monitor, not for the restart policy.
"""

from fastapi import APIRouter, status

from portfolio_api import __version__
from portfolio_api.core.dependencies import DatabaseDep
from portfolio_api.core.errors import DependencyUnavailableError
from portfolio_api.schemas.health import HealthResponse, ReadyResponse

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


@router.get(
    "/readyz",
    response_model=ReadyResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness probe",
    response_description="The instance can serve traffic.",
)
async def readyz(database: DatabaseDep) -> ReadyResponse:
    if not await database.ping():
        raise DependencyUnavailableError("MongoDB is not reachable.")

    return ReadyResponse(status="ready", database="ok")
