"""The profile document.

A singleton: there is one person behind this portfolio. It is stored as a document rather
than hardcoded so the About page reads from the same pipeline as everything else — one
content workflow, not two.
"""

from datetime import UTC, datetime
from typing import Annotated

from beanie import Document, Indexed
from pydantic import BaseModel, Field

# The one and only document key. A unique index on it makes a second profile impossible,
# which is cheaper than a rule everyone has to remember.
PROFILE_KEY = "profile"


class ProfileLinks(BaseModel):
    github: str
    linkedin: str
    cv: str | None = None


class Language(BaseModel):
    name: str
    level: str


class SkillGroup(BaseModel):
    group: str
    items: list[str]


class ExperienceEntry(BaseModel):
    company: str
    role: str
    start: str = Field(pattern=r"^\d{4}-\d{2}$")
    end: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}$")
    summary: str
    highlights: list[str] = Field(default_factory=list)


class EducationEntry(BaseModel):
    institution: str
    degree: str
    start: str = Field(pattern=r"^\d{4}$")
    end: str = Field(pattern=r"^\d{4}$")


class Profile(Document):
    key: Annotated[str, Indexed(unique=True)] = PROFILE_KEY

    name: str
    headline: str = Field(max_length=80)
    location: str
    bio: str
    # Optional on purpose: publishing a personal address invites spam, and the contact form
    # is the intended channel. Omitting it must not break the page.
    email: str | None = None

    links: ProfileLinks
    languages: list[Language] = Field(default_factory=list)
    skills: list[SkillGroup] = Field(default_factory=list)
    experience: list[ExperienceEntry] = Field(default_factory=list)
    education: list[EducationEntry] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)

    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "profile"
