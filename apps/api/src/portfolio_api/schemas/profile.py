"""Wire schemas for the profile."""

from portfolio_api.models.profile import Profile
from portfolio_api.schemas.project import CamelModel


class ProfileLinksResponse(CamelModel):
    github: str
    linkedin: str
    cv: str | None = None


class LanguageResponse(CamelModel):
    name: str
    level: str


class SkillGroupResponse(CamelModel):
    group: str
    items: list[str]


class ExperienceResponse(CamelModel):
    company: str
    role: str
    start: str
    end: str | None = None
    summary: str
    highlights: list[str]


class EducationResponse(CamelModel):
    institution: str
    degree: str
    start: str
    end: str


class ProfileResponse(CamelModel):
    """The public profile.

    The document's `key` and `updated_at` are deliberately absent: they are storage
    mechanics, and every field that leaves the API is a field someone can come to depend on.
    """

    name: str
    headline: str
    location: str
    bio: str
    email: str | None = None
    links: ProfileLinksResponse
    languages: list[LanguageResponse]
    skills: list[SkillGroupResponse]
    experience: list[ExperienceResponse]
    education: list[EducationResponse]
    certifications: list[str]

    @classmethod
    def from_document(cls, profile: Profile) -> "ProfileResponse":
        return cls.model_validate(profile.model_dump())
