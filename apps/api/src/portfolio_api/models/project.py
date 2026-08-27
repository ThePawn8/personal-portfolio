"""The project document — the portfolio's content."""

from datetime import UTC, datetime
from typing import Annotated, Literal

import pymongo
from beanie import Document, Indexed
from pydantic import BaseModel, Field
from pymongo import IndexModel

ProjectKind = Literal["professional", "personal", "open-source", "freelance"]

SUMMARY_MAX_LENGTH = 200
TITLE_MAX_LENGTH = 60


class ProjectPeriod(BaseModel):
    """`YYYY-MM` strings, not dates: month precision is all a portfolio shows."""

    start: str = Field(pattern=r"^\d{4}-\d{2}$")
    end: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}$")


class ProjectLinks(BaseModel):
    live: str | None = None
    repo: str | None = None
    case_study: str | None = None
    video: str | None = None


class Mockup(BaseModel):
    src: str
    alt: str
    caption: str | None = None
    # Intrinsic dimensions are mandatory so the layout can reserve space before the image
    # arrives. Without them every project page shifts as it loads.
    width: int = Field(gt=0)
    height: int = Field(gt=0)


class Metric(BaseModel):
    label: str
    value: str


class Project(Document):
    slug: Annotated[str, Indexed(unique=True)]
    title: str = Field(max_length=TITLE_MAX_LENGTH)
    summary: str = Field(max_length=SUMMARY_MAX_LENGTH)
    # Rendered and sanitised at seed time, never at request time: sanitising once on the way
    # in beats sanitising on every read, and keeps the dangerous step in one place (T-107).
    body_html: str = ""

    kind: ProjectKind
    role: str
    organisation: str | None = None
    period: ProjectPeriod

    stack: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)

    featured: bool = False
    order: int = 100
    published: bool = False
    confidential: bool = False

    links: ProjectLinks = Field(default_factory=ProjectLinks)
    metrics: list[Metric] = Field(default_factory=list)
    mockups: list[Mockup] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "projects"
        indexes = (
            # Covers the list query exactly: filter on published, then sort featured first
            # and by explicit order. One index, no in-memory sort.
            IndexModel(
                [
                    ("published", pymongo.ASCENDING),
                    ("featured", pymongo.DESCENDING),
                    ("order", pymongo.ASCENDING),
                ],
                name="published_featured_order",
            ),
            IndexModel([("tags", pymongo.ASCENDING)], name="tags"),
        )
