"""Content pipeline: authored files in git become documents in MongoDB.

Content is code (ADR-0004). It is reviewed in a pull request, validated in CI, and loaded by
an idempotent upsert. A malformed project fails the build instead of appearing broken in
production.

The seed is deliberately **additive**: it never deletes. Retiring a project means setting
`published: false`, so a file removed by accident cannot silently wipe live content.
"""

from portfolio_api.seed.loader import ContentError, load_projects
from portfolio_api.seed.runner import SeedResult, seed_content

__all__ = ["ContentError", "SeedResult", "load_projects", "seed_content"]
