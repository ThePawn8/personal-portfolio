"""The projects endpoints, end to end against a real MongoDB."""

from typing import Any

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from portfolio_api.models import Project, ProjectPeriod

PROJECTS_URL = "/api/v1/projects"


def build_project(slug: str, **overrides: Any) -> Project:
    defaults: dict[str, Any] = {
        "slug": slug,
        "title": f"Project {slug}",
        "summary": "One sentence that fits on a card.",
        "body_html": f"<p>{slug}</p>",
        "kind": "professional",
        "role": "Frontend Developer",
        "period": ProjectPeriod(start="2024-01", end=None),
        "stack": ["vue"],
        "tags": ["frontend"],
        "published": True,
    }
    return Project(**{**defaults, **overrides})


@pytest.fixture
async def seeded(connected_app: FastAPI) -> FastAPI:
    """Three published projects and one draft, in deliberately unhelpful insertion order."""
    await build_project("second", featured=False, order=20).insert()
    await build_project("headline", featured=True, order=99, tags=["frontend", "vue"]).insert()
    await build_project("first", featured=False, order=10).insert()
    await build_project("draft", published=False, featured=True, order=1).insert()
    return connected_app


async def test_lists_only_published_projects(seeded: FastAPI, db_client: AsyncClient) -> None:
    """A draft must never be reachable, whatever its featured flag or order says."""
    response = await db_client.get(PROJECTS_URL)

    assert response.status_code == 200
    slugs = [project["slug"] for project in response.json()]
    assert "draft" not in slugs
    assert len(slugs) == 3


async def test_sorts_featured_first_then_by_order(seeded: FastAPI, db_client: AsyncClient) -> None:
    response = await db_client.get(PROJECTS_URL)

    # `headline` is featured, so it leads despite having the highest order value.
    assert [project["slug"] for project in response.json()] == ["headline", "first", "second"]


async def test_filters_by_tag(seeded: FastAPI, db_client: AsyncClient) -> None:
    response = await db_client.get(PROJECTS_URL, params={"tag": "vue"})

    assert [project["slug"] for project in response.json()] == ["headline"]


async def test_unknown_tag_returns_an_empty_list_not_an_error(
    seeded: FastAPI,
    db_client: AsyncClient,
) -> None:
    response = await db_client.get(PROJECTS_URL, params={"tag": "cobol"})

    assert response.status_code == 200
    assert response.json() == []


async def test_list_omits_the_case_study_body(seeded: FastAPI, db_client: AsyncClient) -> None:
    """The most-requested endpoint should not ship content nobody asked to read."""
    response = await db_client.get(PROJECTS_URL)

    assert "bodyHtml" not in response.json()[0]


async def test_serialises_in_camel_case(seeded: FastAPI, db_client: AsyncClient) -> None:
    response = await db_client.get(f"{PROJECTS_URL}/headline")

    body = response.json()
    assert "bodyHtml" in body
    assert "body_html" not in body
    assert "caseStudy" in body["links"]


async def test_detail_returns_the_full_project(seeded: FastAPI, db_client: AsyncClient) -> None:
    response = await db_client.get(f"{PROJECTS_URL}/headline")

    assert response.status_code == 200
    body = response.json()
    assert body["slug"] == "headline"
    assert body["bodyHtml"] == "<p>headline</p>"
    assert body["period"] == {"start": "2024-01", "end": None}


async def test_unknown_slug_returns_problem_json(seeded: FastAPI, db_client: AsyncClient) -> None:
    response = await db_client.get(f"{PROJECTS_URL}/nope")

    assert response.status_code == 404
    body = response.json()
    assert body["type"].endswith("#project-not-found")
    assert "nope" in body["detail"]


async def test_draft_slug_is_indistinguishable_from_a_missing_one(
    seeded: FastAPI,
    db_client: AsyncClient,
) -> None:
    """Draft work must not be discoverable by guessing URLs."""
    response = await db_client.get(f"{PROJECTS_URL}/draft")

    assert response.status_code == 404


async def test_malformed_slug_is_rejected_before_the_database(
    seeded: FastAPI,
    db_client: AsyncClient,
) -> None:
    response = await db_client.get(f"{PROJECTS_URL}/Not%20A%20Slug!")

    assert response.status_code == 422
    assert response.json()["type"].endswith("#validation-error")


async def test_responses_are_cacheable(seeded: FastAPI, db_client: AsyncClient) -> None:
    response = await db_client.get(PROJECTS_URL)

    assert response.headers["cache-control"].startswith("public, max-age=300")
    assert response.headers["etag"]


async def test_repeat_request_with_etag_returns_304(
    seeded: FastAPI,
    db_client: AsyncClient,
) -> None:
    """A returning visitor should get an empty body, not the same payload again."""
    first = await db_client.get(PROJECTS_URL)
    etag = first.headers["etag"]

    second = await db_client.get(PROJECTS_URL, headers={"If-None-Match": etag})

    assert second.status_code == 304
    assert second.content == b""
    assert second.headers["etag"] == etag


async def test_etag_survives_a_weak_prefix_from_a_proxy(
    seeded: FastAPI,
    db_client: AsyncClient,
) -> None:
    first = await db_client.get(PROJECTS_URL)
    weak = f"W/{first.headers['etag']}"

    second = await db_client.get(PROJECTS_URL, headers={"If-None-Match": weak})

    assert second.status_code == 304


async def test_etag_changes_when_the_content_changes(
    seeded: FastAPI,
    db_client: AsyncClient,
) -> None:
    """Content-derived, so a redeploy that changes nothing keeps every cache valid."""
    before = (await db_client.get(PROJECTS_URL)).headers["etag"]

    await build_project("late-arrival", order=5).insert()

    after = (await db_client.get(PROJECTS_URL)).headers["etag"]
    assert before != after


async def test_empty_database_returns_an_empty_list(
    connected_app: FastAPI,
    db_client: AsyncClient,
) -> None:
    response = await db_client.get(PROJECTS_URL)

    assert response.status_code == 200
    assert response.json() == []
