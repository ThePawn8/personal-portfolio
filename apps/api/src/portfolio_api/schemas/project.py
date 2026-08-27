"""Wire schemas for projects.

Separate classes from the documents in `models/`, and deliberately so: the stored shape
must be free to gain fields — internal notes, draft flags, timestamps — without any of them
appearing in a public response. Coupling the two is the most common way private data
escapes (ARCHITECTURE § 6.2).

The wire format is camelCase; the documents are snake_case. This is the mapping point.
"""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from portfolio_api.models.project import Project, ProjectKind


class CamelModel(BaseModel):
    """Base for every response model: emits camelCase, accepts either spelling."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class PeriodResponse(CamelModel):
    start: str
    end: str | None = None


class LinksResponse(CamelModel):
    live: str | None = None
    repo: str | None = None
    case_study: str | None = None
    video: str | None = None


class MockupResponse(CamelModel):
    src: str
    alt: str
    caption: str | None = None
    width: int
    height: int


class MetricResponse(CamelModel):
    label: str
    value: str


class ProjectSummaryResponse(CamelModel):
    """What a card needs. The case-study body is deliberately absent.

    The list endpoint is the most requested page on the site; shipping every project's full
    body with it would multiply the payload for content nobody has asked to read yet.
    """

    slug: str
    title: str
    summary: str
    kind: ProjectKind
    role: str
    organisation: str | None = None
    period: PeriodResponse
    stack: list[str]
    tags: list[str]
    featured: bool
    order: int
    confidential: bool
    links: LinksResponse
    metrics: list[MetricResponse]
    mockups: list[MockupResponse]

    @classmethod
    def from_document(cls, project: Project) -> "ProjectSummaryResponse":
        return cls.model_validate(project.model_dump())


class ProjectResponse(ProjectSummaryResponse):
    """A single project, with the rendered case study."""

    body_html: str

    @classmethod
    def from_document(cls, project: Project) -> "ProjectResponse":
        return cls.model_validate(project.model_dump())
