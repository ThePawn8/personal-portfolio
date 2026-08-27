"""Project rules."""

from portfolio_api.core.errors import ProjectNotFoundError
from portfolio_api.repositories import ProjectRepository
from portfolio_api.schemas.project import ProjectResponse, ProjectSummaryResponse


class ProjectService:
    def __init__(self, repository: ProjectRepository) -> None:
        self._repository = repository

    async def list_projects(self, tag: str | None = None) -> list[ProjectSummaryResponse]:
        projects = await self._repository.list_published(tag=tag)
        return [ProjectSummaryResponse.from_document(project) for project in projects]

    async def get_project(self, slug: str) -> ProjectResponse:
        """Fetch one project, or say clearly that it does not exist.

        Raising rather than returning `None` keeps the 404 decision in one place: the router
        does not get to invent a different response for a missing project than the profile
        endpoint does for a missing profile.
        """
        project = await self._repository.get_published_by_slug(slug)
        if project is None:
            raise ProjectNotFoundError(f"No published project exists with slug '{slug}'.")

        return ProjectResponse.from_document(project)
