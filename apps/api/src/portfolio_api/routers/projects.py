"""Project endpoints.

HTTP only: parse the request, delegate, serialise. Every decision about what counts as a
project, what is visible and what a missing one means lives in the service.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request, Response, status

from portfolio_api.core.http_cache import cached_json_response
from portfolio_api.repositories import ProjectRepository
from portfolio_api.schemas.project import ProjectResponse, ProjectSummaryResponse
from portfolio_api.services import ProjectService

router = APIRouter(prefix="/api/v1", tags=["projects"])

SLUG_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"


def get_project_service() -> ProjectService:
    """Assembled per request; the objects are stateless and cheap to build."""
    return ProjectService(ProjectRepository())


ProjectServiceDep = Annotated[ProjectService, Depends(get_project_service)]


@router.get(
    "/projects",
    response_model=list[ProjectSummaryResponse],
    status_code=status.HTTP_200_OK,
    summary="List published projects",
    response_description="Published projects, featured first, then by explicit order.",
)
async def list_projects(
    request: Request,
    service: ProjectServiceDep,
    tag: Annotated[str | None, Query(max_length=40, description="Filter by tag.")] = None,
) -> Response:
    projects = await service.list_projects(tag=tag)
    payload = [project.model_dump(by_alias=True) for project in projects]

    return cached_json_response(request, payload)


@router.get(
    "/projects/{slug}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Get one published project",
    response_description="The project, including its rendered case study.",
)
async def get_project(
    request: Request,
    service: ProjectServiceDep,
    # Constrained at the edge: a slug is a URL segment, and the pattern rejects traversal
    # and injection attempts before anything reaches the database.
    slug: Annotated[str, Path(pattern=SLUG_PATTERN, max_length=100)],
) -> Response:
    project = await service.get_project(slug)

    return cached_json_response(request, project.model_dump(by_alias=True))
