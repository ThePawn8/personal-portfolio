"""Fixed-window rate limiting, stored in MongoDB.

No Redis: one more service to run, pay for and monitor, to protect an endpoint that allows
five requests an hour. A TTL index makes the database expire the buckets itself, so there is
no cleanup job to forget about either.
"""

from datetime import datetime
from typing import Annotated

import pymongo
from beanie import Document, Indexed
from pydantic import Field
from pymongo import IndexModel


class RateLimitBucket(Document):
    """One counter per (client, route, window).

    `key` is `sha256(ip + salt):route:window-start`, so it identifies a client without
    storing anything that identifies a person.
    """

    key: Annotated[str, Indexed(unique=True)]
    # Named `hits` rather than `count`: Beanie's Document already defines `count`, and
    # shadowing it silently changes what `RateLimitBucket.count()` means.
    hits: int = Field(default=0, ge=0)
    expires_at: datetime

    class Settings:
        name = "rate_limits"
        indexes = (
            # expireAfterSeconds=0 means "delete when expires_at passes" — MongoDB does the
            # housekeeping, and an abandoned deployment cannot accumulate junk.
            IndexModel([("expires_at", pymongo.ASCENDING)], name="ttl", expireAfterSeconds=0),
        )
