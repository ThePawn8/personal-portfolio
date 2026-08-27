"""Command line entry point: `python -m portfolio_api.seed`.

Three modes, in increasing order of consequence:

  --check      validate the files and exit. No database needed, so CI can gate a content
               pull request without spinning one up.
  --dry-run    connect and report what would change, without writing.
  (default)    upsert.
"""

import argparse
import asyncio
import sys
from pathlib import Path

from portfolio_api.core.config import get_settings
from portfolio_api.core.database import Database
from portfolio_api.core.logging import configure_logging
from portfolio_api.seed.loader import ContentError, load_profile, load_projects
from portfolio_api.seed.runner import seed_content

# seed/__main__.py -> portfolio_api -> src -> api -> apps -> repository root.
DEFAULT_CONTENT_DIR = Path(__file__).resolve().parents[5] / "content"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m portfolio_api.seed",
        description="Load content/ into MongoDB. Idempotent, and never deletes.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate the content files and exit without touching the database",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="report what would change without writing",
    )
    parser.add_argument(
        "--content-dir",
        type=Path,
        default=DEFAULT_CONTENT_DIR,
        help=f"content directory (default: {DEFAULT_CONTENT_DIR})",
    )
    return parser.parse_args(argv)


async def _seed(content_dir: Path, *, dry_run: bool) -> int:
    settings = get_settings()
    database = Database(uri=settings.mongodb_uri, name=settings.mongodb_db)

    await database.connect()
    try:
        result = await seed_content(content_dir, dry_run=dry_run)
    finally:
        await database.disconnect()

    verb = "would create/update" if dry_run else "created/updated"
    profile_state = "written" if result.profile_written else "unchanged"
    print(  # noqa: T201
        f"{verb}: {len(result.created)} new, {len(result.updated)} changed, "
        f"{len(result.unchanged)} unchanged ({result.total} total); "
        f"profile {profile_state}"
    )
    for slug in result.created:
        print(f"  + {slug}")  # noqa: T201
    for slug in result.updated:
        print(f"  ~ {slug}")  # noqa: T201

    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    configure_logging(level="INFO", json_output=False)

    try:
        if args.check:
            projects = load_projects(args.content_dir)
            profile = load_profile(args.content_dir)
            published = sum(1 for project in projects if project.published)
            print(  # noqa: T201
                f"profile for {profile.name} valid; "
                f"{len(projects)} project(s) valid, {published} published"
            )
            return 0

        return asyncio.run(_seed(args.content_dir, dry_run=args.dry_run))

    except ContentError as error:
        # Named file, named field: the author should not have to guess.
        print(f"content error -> {error}", file=sys.stderr)  # noqa: T201
        return 1
    except FileNotFoundError as error:
        print(f"error -> {error}", file=sys.stderr)  # noqa: T201
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
