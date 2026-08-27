"""Project queries."""

from portfolio_api.models import Project


class ProjectRepository:
    """Reads published projects.

    There is no `list_all`: nothing in the public API may return an unpublished project, and
    the safest way to guarantee that is to never build the query that could.
    """

    async def list_published(self, tag: str | None = None) -> list[Project]:
        """Published projects, featured first, then by explicit order.

        The sort matches the compound index exactly (`published`, `featured` descending,
        `order`), so MongoDB walks the index instead of sorting in memory.
        """
        # Beanie builds its query from the comparison operator, so `== True` is required
        # here; `is True` would evaluate in Python and produce a boolean, not a query.
        query = Project.find(Project.published == True)  # noqa: E712

        if tag is not None:
            # A raw filter rather than `Project.tags == tag`: in MongoDB, comparing an array
            # field to a scalar means "contains", but to a type checker it reads as
            # `list[str] == str` and is flagged as an impossible comparison. The dict says
            # what is actually sent to the server.
            query = query.find({"tags": tag})

        return await query.sort("-featured", "+order").to_list()

    async def get_published_by_slug(self, slug: str) -> Project | None:
        """One published project.

        An unpublished project is indistinguishable from a missing one by design: draft work
        must not be discoverable by guessing URLs.
        """
        return await Project.find_one(Project.slug == slug, Project.published == True)  # noqa: E712
