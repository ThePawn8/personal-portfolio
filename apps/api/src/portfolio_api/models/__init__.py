"""Persistence documents.

Deliberately separate from the wire schemas in `schemas/`: the stored shape must be free to
gain fields — timestamps, internal notes, draft flags — without any of them leaking into a
public response (ARCHITECTURE § 6.2).
"""

from beanie import Document

from portfolio_api.models.message import Message
from portfolio_api.models.project import Metric, Mockup, Project, ProjectLinks, ProjectPeriod
from portfolio_api.models.rate_limit import RateLimitBucket

# Registered with Beanie at startup; this is also the list whose indexes get created.
DOCUMENT_MODELS: list[type[Document]] = [Project, Message, RateLimitBucket]

__all__ = [
    "DOCUMENT_MODELS",
    "Message",
    "Metric",
    "Mockup",
    "Project",
    "ProjectLinks",
    "ProjectPeriod",
    "RateLimitBucket",
]
