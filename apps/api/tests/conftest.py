"""Shared test fixtures."""

from collections.abc import AsyncIterator, Callable
from typing import Any

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from portfolio_api.core.config import Settings
from portfolio_api.main import create_app

# 64 hex characters, the same shape `npm run setup` generates.
TEST_SALT = "a" * 64

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
def settings(build_settings: SettingsFactory) -> Settings:
    return build_settings(
        app_env="local",
        log_level="INFO",
        ip_hash_salt=TEST_SALT,
        cors_allowed_origins=["http://localhost:5173"],
    )


@pytest.fixture
def app(settings: Settings) -> FastAPI:
    """A fresh application per test, so no test can leak state into another."""
    return create_app(settings)


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    """HTTP client that talks to the app in-process, without binding a port."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client
