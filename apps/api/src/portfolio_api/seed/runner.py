"""Writing validated content into MongoDB."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel

from portfolio_api.core.logging import get_logger
from portfolio_api.models import Profile, Project
from portfolio_api.models.profile import (
    PROFILE_KEY,
    EducationEntry,
    ExperienceEntry,
    Language,
    ProfileLinks,
    SkillGroup,
)
from portfolio_api.models.project import Metric, Mockup, ProjectLinks, ProjectPeriod
from portfolio_api.seed.loader import (
    ProfileContent,
    ProjectContent,
    load_profile,
    load_projects,
)

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
    profile_written: bool = False

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

    result.profile_written = await _seed_profile(content_dir, dry_run=dry_run)

    logger.info(
        "seed_completed",
        created=len(result.created),
        updated=len(result.updated),
        unchanged=len(result.unchanged),
        profile_written=result.profile_written,
        dry_run=dry_run,
    )
    return result


def _to_profile_fields(content: ProfileContent) -> dict[str, object]:
    return {
        "name": content.name,
        "headline": content.headline,
        "location": content.location,
        "bio": content.bio.strip(),
        "email": content.email,
        "links": ProfileLinks(**content.links.model_dump()),
        "languages": [Language(**item.model_dump()) for item in content.languages],
        "skills": [SkillGroup(**item.model_dump()) for item in content.skills],
        "experience": [ExperienceEntry(**item.model_dump()) for item in content.experience],
        "education": [EducationEntry(**item.model_dump()) for item in content.education],
        "certifications": content.certifications,
    }


async def _seed_profile(content_dir: Path, *, dry_run: bool) -> bool:
    """Upsert the single profile document. Returns whether anything changed."""
    fields = _to_profile_fields(load_profile(content_dir))
    existing = await Profile.find_one(Profile.key == PROFILE_KEY)

    unchanged = existing is not None and not any(
        _normalise(getattr(existing, name)) != _normalise(value) for name, value in fields.items()
    )
    if unchanged:
        return False

    if dry_run:
        return True

    if existing is None:
        await Profile(key=PROFILE_KEY, **fields).insert()
    else:
        for name, value in fields.items():
            setattr(existing, name, value)
        existing.updated_at = datetime.now(UTC)
        await existing.save()

    return True
