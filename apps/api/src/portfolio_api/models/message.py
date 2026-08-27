"""Contact messages.

Persisted before any email is attempted, so a failure at the email provider loses a
notification but never the message itself (T-106).
"""

from datetime import UTC, datetime
from typing import Literal

import pymongo
from beanie import Document
from pydantic import Field
from pymongo import IndexModel

MessageStatus = Literal["received", "notified", "failed"]


class Message(Document):
    name: str
    email: str
    body: str

    # A SHA-256 of the visitor's IP, never the address itself. Rate limiting needs a stable
    # per-client key, not an identity, so the store stays free of personal data by
    # construction (ARCHITECTURE § 7).
    source_ip_hash: str
    user_agent: str | None = None

    status: MessageStatus = "received"
    error: str | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "messages"
        indexes = (IndexModel([("created_at", pymongo.DESCENDING)], name="created_at_desc"),)
