"""Shared test fixtures."""

import os
from collections.abc import AsyncIterator, Callable
from typing import Any
from uuid import uuid4

import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pymongo import AsyncMongoClient

from portfolio_api.core.config import Settings
from portfolio_api.main import create_app

# 64 hex characters, the same shape `npm run setup` generates.
TEST_SALT = "a" * 64

# A real MongoDB. Integration tests are not run against a mock: a mocked database proves
# the mock works, not that the queries, indexes or unique constraints do.
MONGODB_TEST_URI = os.environ.get("MONGODB_TEST_URI", "mongodb://127.0.0.1:27017")

SettingsFactory = Callable[..., Settings]


@pytest.fixture
def build_settings() -> SettingsFactory:
    """Build settings isolated from any `.env` file on the machine.

    A developer with a populated `.env` and CI with none must run the same tests, so the
    env file is disabled explicitly. pydantic-settings accepts `_env_file` at runtime but
    does not declare it on the generated `__init__`, hence the single suppression — kept
    here, once, rather than repeated in every test.
    """

    def _build(**overrides: Any) -> Settings:
        return Settings(_env_file=None, **overrides)  # type: ignore[call-arg]

    return _build


@pytest.fixture
def database_name() -> str:
    """A private database per test, so tests cannot see each other's documents."""
    return f"portfolio_test_{uuid4().hex[:12]}"


@pytest.fixture
def settings(build_settings: SettingsFactory, database_name: str) -> Settings:
    return build_settings(
        app_env="local",
        log_level="INFO",
        ip_hash_salt=TEST_SALT,
        cors_allowed_origins=["http://localhost:5173"],
        mongodb_uri=MONGODB_TEST_URI,
        mongodb_db=database_name,
    )


@pytest.fixture
def app(settings: Settings) -> FastAPI:
    """A fresh application per test, so no test can leak state into another."""
    return create_app(settings)


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    """HTTP client for tests that need no database.

    `ASGITransport` skips the lifespan, so nothing connects to MongoDB here.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client


@pytest.fixture
async def connected_app(app: FastAPI, database_name: str) -> AsyncIterator[FastAPI]:
    """The application with its lifespan run: MongoDB connected, indexes created."""
    async with LifespanManager(app):
        yield app

    # The app closed its own client on shutdown, so cleanup needs its own connection.
    cleanup_client: AsyncMongoClient[dict[str, Any]] = AsyncMongoClient(MONGODB_TEST_URI)
    try:
        await cleanup_client.drop_database(database_name)
    finally:
        await cleanup_client.close()


@pytest.fixture
async def db_client(connected_app: FastAPI) -> AsyncIterator[AsyncClient]:
    """HTTP client backed by a real, empty database."""
    transport = ASGITransport(app=connected_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client
