"""Writing validated content into MongoDB."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel

from portfolio_api.core.logging import get_logger
from portfolio_api.models import Project
from portfolio_api.models.project import Metric, Mockup, ProjectLinks, ProjectPeriod
from portfolio_api.seed.loader import ProjectContent, load_projects

logger = get_logger(__name__)

# Fields the seed owns. Anything else on the document — timestamps, future internal
# fields — is left alone, so the seed cannot clobber state it does not author.
SEEDED_FIELDS = (
    "title",
    "summary",
    "body_html",
    "kind",
    "role",
    "organisation",
    "period",
    "stack",
    "tags",
    "published",
    "featured",
    "order",
    "confidential",
    "links",
    "metrics",
    "mockups",
)


@dataclass
class SeedResult:
    created: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.created) + len(self.updated) + len(self.unchanged)


def _to_document_fields(content: ProjectContent) -> dict[str, object]:
    return {
        "title": content.title,
        "summary": content.summary,
        "body_html": content.body_html,
        "kind": content.kind,
        "role": content.role,
        "organisation": content.organisation,
        "period": ProjectPeriod(start=content.period.start, end=content.period.end),
        "stack": content.stack,
        "tags": content.tags,
        "published": content.published,
        "featured": content.featured,
        "order": content.order,
        "confidential": content.confidential,
        "links": ProjectLinks(**content.links.model_dump()),
        "metrics": [Metric(**metric.model_dump()) for metric in content.metrics],
        "mockups": [Mockup(**mockup.model_dump()) for mockup in content.mockups],
    }


def _normalise(value: object) -> object:
    """Reduce a field to plain data so two versions can be compared by value.

    Nested Pydantic models compare by identity often enough to make a naive `!=` report
    every project as changed on every run, which would defeat the whole point of the
    unchanged/updated distinction.
    """
    if isinstance(value, BaseModel):
        return value.model_dump()
    if isinstance(value, list):
        return [_normalise(item) for item in value]
    return value


def _differs(existing: Project, fields: dict[str, object]) -> bool:
    """Whether the stored document says something different from the authored file."""
    return any(
        _normalise(getattr(existing, name)) != _normalise(fields[name]) for name in SEEDED_FIELDS
    )


async def seed_content(content_dir: Path, *, dry_run: bool = False) -> SeedResult:
    """Load `content/` and upsert it, reporting what actually changed.

    Idempotent by construction: a second run finds every document identical and writes
    nothing, which also keeps `updated_at` meaningful instead of tracking deploy times.
    """
    projects = load_projects(content_dir)
    result = SeedResult()

    for content in projects:
        fields = _to_document_fields(content)
        existing = await Project.find_one(Project.slug == content.slug)

        if existing is None:
            result.created.append(content.slug)
            if not dry_run:
                await Project(slug=content.slug, **fields).insert()
            continue

        if not _differs(existing, fields):
            result.unchanged.append(content.slug)
            continue

        result.updated.append(content.slug)
        if not dry_run:
            for name, value in fields.items():
                setattr(existing, name, value)
            existing.updated_at = datetime.now(UTC)
            await existing.save()

    logger.info(
        "seed_completed",
        created=len(result.created),
        updated=len(result.updated),
        unchanged=len(result.unchanged),
        dry_run=dry_run,
    )
    return result
