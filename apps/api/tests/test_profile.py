"""The profile endpoint."""

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from portfolio_api.models import Profile
from portfolio_api.models.profile import (
    EducationEntry,
    ExperienceEntry,
    Language,
    ProfileLinks,
    SkillGroup,
)

PROFILE_URL = "/api/v1/profile"


def build_profile(**overrides: object) -> Profile:
    defaults: dict[str, object] = {
        "name": "Andrés M",
        "headline": "Frontend Developer",
        "location": "Manizales, Colombia",
        "bio": "A short bio.",
        "links": ProfileLinks(github="https://github.com/x", linkedin="https://linkedin.com/in/x"),
        "languages": [Language(name="Spanish", level="Native")],
        "skills": [SkillGroup(group="Frontend", items=["Vue.js", "TypeScript"])],
        "experience": [
            ExperienceEntry(
                company="Anglus",
                role="Development Engineer",
                start="2014-03",
                end="2018-11",
                summary="Frontend and backend.",
                highlights=[],
            ),
            ExperienceEntry(
                company="NICE",
                role="Frontend Developer",
                start="2024-06",
                end=None,
                summary="Frontend development.",
                highlights=["Shipped things"],
            ),
        ],
        "education": [
            EducationEntry(
                institution="Universidad de Caldas",
                degree="Systems and Computing Engineering",
                start="2008",
                end="2014",
            )
        ],
        "certifications": ["Curso Profesional de Vue.js"],
    }
    return Profile(**{**defaults, **overrides})


@pytest.fixture
async def seeded_profile(connected_app: FastAPI) -> FastAPI:
    await build_profile().insert()
    return connected_app


async def test_returns_the_profile(seeded_profile: FastAPI, db_client: AsyncClient) -> None:
    response = await db_client.get(PROFILE_URL)

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Andrés M"
    assert body["links"]["github"] == "https://github.com/x"
    assert body["certifications"] == ["Curso Profesional de Vue.js"]


async def test_experience_is_newest_first(
    seeded_profile: FastAPI,
    db_client: AsyncClient,
) -> None:
    """A CV that opens with a job from 2014 reads as a mistake."""
    response = await db_client.get(PROFILE_URL)

    companies = [entry["company"] for entry in response.json()["experience"]]
    assert companies == ["NICE", "Anglus"]


async def test_omits_storage_mechanics(seeded_profile: FastAPI, db_client: AsyncClient) -> None:
    """Every field that leaves the API is one somebody can come to depend on."""
    body = (await db_client.get(PROFILE_URL)).json()

    assert "key" not in body
    assert "updatedAt" not in body
    assert "_id" not in body
    assert "id" not in body


async def test_omitted_email_is_null_not_missing(
    seeded_profile: FastAPI,
    db_client: AsyncClient,
) -> None:
    """The client should not have to distinguish "absent" from "not published"."""
    body = (await db_client.get(PROFILE_URL)).json()

    assert body["email"] is None


async def test_published_email_is_returned(connected_app: FastAPI, db_client: AsyncClient) -> None:
    await build_profile(email="hello@example.com").insert()

    body = (await db_client.get(PROFILE_URL)).json()

    assert body["email"] == "hello@example.com"


async def test_missing_profile_is_a_404_not_an_empty_object(
    connected_app: FastAPI,
    db_client: AsyncClient,
) -> None:
    """An unseeded profile is a deployment failure; an empty object would hide it."""
    response = await db_client.get(PROFILE_URL)

    assert response.status_code == 404
    assert response.json()["type"].endswith("#profile-not-found")


async def test_response_is_cacheable(seeded_profile: FastAPI, db_client: AsyncClient) -> None:
    response = await db_client.get(PROFILE_URL)

    assert response.headers["cache-control"].startswith("public, max-age=300")

    conditional = await db_client.get(
        PROFILE_URL,
        headers={"If-None-Match": response.headers["etag"]},
    )
    assert conditional.status_code == 304
