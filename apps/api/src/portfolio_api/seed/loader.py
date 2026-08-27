"""Reading and validating authored content.

The schema here is the contract documented in `content/README.md`. Unknown fields are a
hard error: a typo in frontmatter should fail the build, not silently drop the value and
leave the author wondering why their change did nothing.
"""

import re
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from portfolio_api.models.project import SUMMARY_MAX_LENGTH, TITLE_MAX_LENGTH, ProjectKind
from portfolio_api.seed.renderer import render_markdown

FRONTMATTER_PATTERN = re.compile(r"^---\r?\n(?P<frontmatter>.*?)\r?\n---\r?\n(?P<body>.*)$", re.S)

# Files starting with `_` are the template and the worked example. They are never published,
# whatever their frontmatter says.
PRIVATE_PREFIX = "_"


class ContentError(Exception):
    """A content file that cannot be published, with enough detail to fix it."""

    def __init__(self, path: Path, message: str) -> None:
        self.path = path
        super().__init__(f"{path.name}: {message}")


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PeriodContent(StrictModel):
    start: str = Field(pattern=r"^\d{4}-\d{2}$")
    end: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}$")


class LinksContent(StrictModel):
    live: str | None = None
    repo: str | None = None
    case_study: str | None = None
    video: str | None = None


class MockupContent(StrictModel):
    src: str
    alt: str = Field(min_length=1)
    caption: str | None = None
    width: int = Field(gt=0)
    height: int = Field(gt=0)


class MetricContent(StrictModel):
    label: str
    value: str


class ProjectContent(StrictModel):
    """One project as authored. Mirrors `content/README.md` field for field."""

    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    title: str = Field(max_length=TITLE_MAX_LENGTH)
    summary: str = Field(max_length=SUMMARY_MAX_LENGTH)
    kind: ProjectKind
    role: str
    organisation: str | None = None
    period: PeriodContent
    stack: list[str] = Field(min_length=1)
    tags: list[str] = Field(min_length=1)
    published: bool
    featured: bool = False
    order: int = 100
    confidential: bool = False
    links: LinksContent = Field(default_factory=LinksContent)
    metrics: list[MetricContent] = Field(default_factory=list, max_length=4)
    mockups: list[MockupContent] = Field(default_factory=list)

    # Filled from the Markdown body, not from frontmatter.
    body_html: str = ""


def parse_project_file(path: Path) -> ProjectContent:
    """Parse one `content/projects/*.md` file into a validated project."""
    raw = path.read_text(encoding="utf-8")

    match = FRONTMATTER_PATTERN.match(raw)
    if match is None:
        raise ContentError(path, "no YAML frontmatter block found (expected a leading '---')")

    try:
        frontmatter = yaml.safe_load(match.group("frontmatter"))
    except yaml.YAMLError as error:
        raise ContentError(path, f"frontmatter is not valid YAML: {error}") from error

    if not isinstance(frontmatter, dict):
        raise ContentError(path, "frontmatter must be a mapping of fields")

    # Comments and nulls are legitimate in the template; drop keys the author left empty so
    # optional fields fall back to their defaults instead of failing validation.
    cleaned = {key: value for key, value in frontmatter.items() if value is not None}
    if "links" in cleaned and isinstance(cleaned["links"], dict):
        cleaned["links"] = {k: v for k, v in cleaned["links"].items() if v is not None}

    try:
        content = ProjectContent(**cleaned)
    except ValidationError as error:
        details = "; ".join(
            f"{'.'.join(str(part) for part in issue['loc'])}: {issue['msg']}"
            for issue in error.errors()
        )
        raise ContentError(path, details) from error

    if content.slug != path.stem:
        raise ContentError(path, f"slug '{content.slug}' does not match the filename")

    content.body_html = render_markdown(match.group("body"))
    return content


def load_projects(content_dir: Path) -> list[ProjectContent]:
    """Parse every publishable project file, in a stable order.

    Raises on the first invalid file rather than collecting errors: a broken content file is
    a stop-the-line problem, and the first message is the one worth reading.
    """
    projects_dir = content_dir / "projects"
    if not projects_dir.is_dir():
        message = f"content directory not found: {projects_dir}"
        raise FileNotFoundError(message)

    paths = sorted(
        path for path in projects_dir.glob("*.md") if not path.name.startswith(PRIVATE_PREFIX)
    )

    projects = [parse_project_file(path) for path in paths]

    slugs = [project.slug for project in projects]
    duplicates = {slug for slug in slugs if slugs.count(slug) > 1}
    if duplicates:
        message = f"duplicate slugs: {', '.join(sorted(duplicates))}"
        raise ContentError(projects_dir, message)

    return projects
