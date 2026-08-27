"""Data access.

Every MongoDB query in the application lives in this package. Nothing above it imports the
driver, which is what keeps the query surface small enough to review and lets a service be
tested without a database when that is useful.
"""

from portfolio_api.repositories.profile import ProfileRepository
from portfolio_api.repositories.projects import ProjectRepository

__all__ = ["ProfileRepository", "ProjectRepository"]
