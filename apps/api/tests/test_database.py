"""MongoDB connection, document mapping and index declarations.

These run against a real MongoDB. A mocked database would prove the mock works; unique
constraints, TTL expiry and compound index shapes only exist in the server.
"""

from datetime import UTC, datetime, timedelta

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from pymongo.errors import DuplicateKeyError

from portfolio_api.core.database import Database, DatabaseNotConnectedError
from portfolio_api.models import Message, Project, ProjectPeriod, RateLimitBucket


def make_project(slug: str = "example", **overrides: object) -> Project:
    defaults: dict[str, object] = {
        "slug": slug,
        "title": "Example project",
        "summary": "One sentence that fits on a card.",
        "kind": "professional",
        "role": "Frontend Developer",
        "period": ProjectPeriod(start="2024-01", end=None),
    }
    return Project(**{**defaults, **overrides})


async def test_client_is_unusable_before_the_lifespan_runs() -> None:
    """Using the database before startup is a programming error, not a runtime surprise."""
    database = Database(uri="mongodb://127.0.0.1:27017", name="unused")

    assert database.is_connected is False
    with pytest.raises(DatabaseNotConnectedError):
        _ = database.client


async def test_ping_is_false_when_disconnected() -> None:
    """The readiness probe must get an answer, not an exception."""
    database = Database(uri="mongodb://127.0.0.1:27017", name="unused")

    assert await database.ping() is False


async def test_lifespan_connects_and_disconnects(connected_app: FastAPI) -> None:
    database: Database = connected_app.state.database

    assert database.is_connected is True
    assert await database.ping() is True


async def test_declared_indexes_exist(connected_app: FastAPI) -> None:
    """Indexes are created at startup, so a fresh deployment needs no migration step."""
    database: Database = connected_app.state.database
    db = database.client[connected_app.state.settings.mongodb_db]

    project_indexes = await db["projects"].index_information()
    assert "published_featured_order" in project_indexes
    assert "tags" in project_indexes
    assert any(index.get("unique") for index in project_indexes.values())

    message_indexes = await db["messages"].index_information()
    assert "created_at_desc" in message_indexes

    rate_limit_indexes = await db["rate_limits"].index_information()
    assert rate_limit_indexes["ttl"]["expireAfterSeconds"] == 0


async def test_projects_round_trip(connected_app: FastAPI) -> None:
    await make_project(slug="round-trip").insert()

    stored = await Project.find_one(Project.slug == "round-trip")

    assert stored is not None
    assert stored.title == "Example project"
    # Defaults matter: an unpublished project must never appear by accident.
    assert stored.published is False
    assert stored.order == 100
    assert stored.created_at.tzinfo is not None


async def test_slug_is_unique(connected_app: FastAPI) -> None:
    """The database enforces it, not just the seed script."""
    await make_project(slug="duplicate").insert()

    with pytest.raises(DuplicateKeyError):
        await make_project(slug="duplicate").insert()


async def test_summary_length_is_capped() -> None:
    """A summary that does not fit a card is a content bug, caught at validation time."""
    with pytest.raises(ValueError, match="at most 200 characters"):
        make_project(summary="x" * 201)


async def test_mockups_require_intrinsic_dimensions() -> None:
    """Missing width and height are what make a gallery shift while it loads."""
    with pytest.raises(ValueError, match="width"):
        make_project(mockups=[{"src": "a.png", "alt": "A", "height": 100}])


async def test_messages_store_a_hash_not_an_address(connected_app: FastAPI) -> None:
    message = Message(
        name="Visitor",
        email="visitor@example.com",
        body="Hello",
        source_ip_hash="0" * 64,
        user_agent="pytest",
    )
    await message.insert()

    stored = await Message.find_one(Message.email == "visitor@example.com")

    assert stored is not None
    assert stored.status == "received"
    # The raw address must not be recoverable from the document.
    assert not hasattr(stored, "source_ip")
    assert len(stored.source_ip_hash) == 64


async def test_rate_limit_buckets_carry_an_expiry(connected_app: FastAPI) -> None:
    expires_at = datetime.now(UTC) + timedelta(hours=1)
    await RateLimitBucket(key="hash:contact:1", hits=1, expires_at=expires_at).insert()

    stored = await RateLimitBucket.find_one(RateLimitBucket.key == "hash:contact:1")

    assert stored is not None
    assert stored.expires_at > datetime.now(UTC)


async def test_readyz_reports_ready_when_the_database_answers(db_client: AsyncClient) -> None:
    response = await db_client.get("/readyz")

    assert response.status_code == 200
    assert response.json() == {"status": "ready", "database": "ok"}


async def test_readyz_fails_when_the_database_is_unreachable(
    connected_app: FastAPI,
    db_client: AsyncClient,
) -> None:
    """A 503 with the standard error shape, not a 500 with a stack trace."""
    await connected_app.state.database.disconnect()

    response = await db_client.get("/readyz")

    assert response.status_code == 503
    body = response.json()
    assert body["type"].endswith("#dependency-unavailable")
    assert body["requestId"]


async def test_healthz_stays_green_while_the_database_is_down(
    connected_app: FastAPI,
    db_client: AsyncClient,
) -> None:
    """Liveness must not follow the database.

    If it did, a database outage would make the platform restart healthy containers and
    turn a degraded read path into a full outage.
    """
    await connected_app.state.database.disconnect()

    response = await db_client.get("/healthz")

    assert response.status_code == 200
