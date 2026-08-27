"""Business rules.

Routers parse and serialise; repositories query. Whatever is left — the decisions — lives
here, where it can be tested without an HTTP client or a database session.
"""

from portfolio_api.services.projects import ProjectService

__all__ = ["ProjectService"]
