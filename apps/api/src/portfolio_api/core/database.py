"""MongoDB connection lifecycle.

One client per process, opened at startup and closed at shutdown. The client owns a
connection pool, so creating one per request — the mistake serverless deployments make —
would open and discard connections against a single-node database that handles that badly
(ARCHITECTURE § 4).
"""

from typing import Any

from beanie import init_beanie
from pymongo import AsyncMongoClient
from pymongo.errors import PyMongoError

from portfolio_api.core.logging import get_logger
from portfolio_api.models import DOCUMENT_MODELS

logger = get_logger(__name__)

# Fail fast when the database is unreachable: a request that hangs for 30 seconds is worse
# for the caller than one that fails in 5 and lets the UI fall back to cached content.
SERVER_SELECTION_TIMEOUT_MS = 5000


class DatabaseNotConnectedError(RuntimeError):
    """Raised when the database is used before the application lifespan has run."""

    def __init__(self) -> None:
        super().__init__("Database is not connected: the application lifespan has not run.")


class Database:
    """Owns the MongoDB client and the Beanie registration for its document models.

    An instance rather than module-level globals: tests build an isolated database per
    case, which is what makes the integration suite safe to run in parallel.
    """

    def __init__(self, uri: str, name: str) -> None:
        self._uri = uri
        self._name = name
        self._client: AsyncMongoClient[dict[str, Any]] | None = None

    @property
    def client(self) -> AsyncMongoClient[dict[str, Any]]:
        if self._client is None:
            raise DatabaseNotConnectedError
        return self._client

    @property
    def is_connected(self) -> bool:
        return self._client is not None

    async def connect(self) -> None:
        """Open the pool and register the document models.

        `init_beanie` creates the declared indexes, so a fresh deployment converges on the
        right shape without a migration step — the schema lives with the models.
        """
        self._client = AsyncMongoClient(
            self._uri,
            serverSelectionTimeoutMS=SERVER_SELECTION_TIMEOUT_MS,
            tz_aware=True,
        )
        await init_beanie(database=self._client[self._name], document_models=DOCUMENT_MODELS)
        logger.info("database_connected", database=self._name)

    async def disconnect(self) -> None:
        if self._client is None:
            return
        await self._client.close()
        self._client = None
        logger.info("database_disconnected")

    async def ping(self) -> bool:
        """Whether the database answers right now.

        Returns a boolean rather than raising: the caller is a readiness probe, and an
        unreachable database is an expected state there, not an exception.
        """
        if self._client is None:
            return False
        try:
            await self._client.admin.command("ping")
        except PyMongoError as error:
            logger.warning("database_ping_failed", error=str(error))
            return False
        return True
