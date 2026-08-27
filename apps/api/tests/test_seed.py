"""The content pipeline: authored files become documents, safely and repeatably."""

from pathlib import Path

import pytest
from fastapi import FastAPI

from portfolio_api.models import Profile, Project
from portfolio_api.seed import ContentError, load_profile, load_projects, seed_content
from portfolio_api.seed.__main__ import DEFAULT_CONTENT_DIR, main, parse_args
from portfolio_api.seed.loader import parse_project_file
from portfolio_api.seed.renderer import render_markdown
from portfolio_api.seed.runner import SeedResult

VALID_PROJECT = """---
slug: example-project
title: Example Project
summary: One sentence under two hundred characters.
kind: professional
role: Frontend Developer
organisation: Example Corp
period:
  start: '2023-03'
  end: '2024-02'
stack: [vue, typescript]
tags: [frontend, performance]
published: true
featured: true
order: 10
links:
  live: https://example.com
  repo: null
metrics:
  - label: Time to first reply
    value: '-34%'
mockups:
  - src: example-project/hero.png
    alt: A screenshot of the inbox
    width: 1600
    height: 900
---

## Context

The **situation** and the problem.

## Impact

Time to first reply dropped by a third.
"""


def write_project(directory: Path, name: str, body: str) -> Path:
    projects = directory / "projects"
    projects.mkdir(parents=True, exist_ok=True)
    path = projects / name
    path.write_text(body, encoding="utf-8")

    # `seed_content` loads projects and the profile together, so a fixture directory needs
    # both to exist. Written here so every test does not have to remember.
    profile = directory / "profile.yml"
    if not profile.exists():
        profile.write_text(VALID_PROFILE, encoding="utf-8")

    return path


class TestRenderer:
    def test_renders_markdown_structure(self) -> None:
        html = render_markdown("## Heading\n\nSome **bold** text.")

        assert "<h2>Heading</h2>" in html
        assert "<strong>bold</strong>" in html

    def test_strips_script_tags(self) -> None:
        """A script in a content file must not survive into a page."""
        html = render_markdown("Hello\n\n<script>alert('xss')</script>")

        assert "script" not in html
        assert "alert" not in html

    def test_strips_event_handlers_and_iframes(self) -> None:
        html = render_markdown('<img src="x" onerror="alert(1)">\n\n<iframe src="evil"></iframe>')

        assert "onerror" not in html
        assert "iframe" not in html

    def test_external_links_cannot_reach_back_through_opener(self) -> None:
        html = render_markdown("[link](https://example.com)")

        assert 'rel="noopener noreferrer"' in html


class TestLoader:
    def test_parses_a_valid_project(self, tmp_path: Path) -> None:
        path = write_project(tmp_path, "example-project.md", VALID_PROJECT)

        project = parse_project_file(path)

        assert project.slug == "example-project"
        assert project.published is True
        assert project.stack == ["vue", "typescript"]
        assert project.metrics[0].value == "-34%"
        assert project.mockups[0].width == 1600
        assert "<h2>Context</h2>" in project.body_html
        # Nulls in frontmatter fall back to defaults instead of failing validation.
        assert project.links.repo is None
        assert project.links.live == "https://example.com"

    def test_rejects_a_missing_frontmatter_block(self, tmp_path: Path) -> None:
        path = write_project(tmp_path, "broken.md", "# Just a heading\n")

        with pytest.raises(ContentError, match="no YAML frontmatter"):
            parse_project_file(path)

    def test_rejects_invalid_yaml(self, tmp_path: Path) -> None:
        path = write_project(tmp_path, "broken.md", "---\ntitle: [unclosed\n---\n\nBody\n")

        with pytest.raises(ContentError, match="not valid YAML"):
            parse_project_file(path)

    def test_names_the_offending_field(self, tmp_path: Path) -> None:
        """The author should not have to guess which field is wrong."""
        content = VALID_PROJECT.replace("kind: professional", "kind: made-up")
        path = write_project(tmp_path, "example-project.md", content)

        with pytest.raises(ContentError, match="kind"):
            parse_project_file(path)

    def test_rejects_an_unknown_field(self, tmp_path: Path) -> None:
        """A typo should fail the build, not silently drop the value."""
        content = VALID_PROJECT.replace("featured: true", "featured: true\nfeatrued: true")
        path = write_project(tmp_path, "example-project.md", content)

        with pytest.raises(ContentError, match="featrued"):
            parse_project_file(path)

    def test_rejects_a_summary_that_will_not_fit_a_card(self, tmp_path: Path) -> None:
        content = VALID_PROJECT.replace(
            "summary: One sentence under two hundred characters.",
            f"summary: {'x' * 201}",
        )
        path = write_project(tmp_path, "example-project.md", content)

        with pytest.raises(ContentError, match="summary"):
            parse_project_file(path)

    def test_rejects_a_mockup_without_dimensions(self, tmp_path: Path) -> None:
        content = VALID_PROJECT.replace("    width: 1600\n", "")
        path = write_project(tmp_path, "example-project.md", content)

        with pytest.raises(ContentError, match="width"):
            parse_project_file(path)

    def test_requires_the_filename_to_match_the_slug(self, tmp_path: Path) -> None:
        """The filename is the URL; a mismatch means the file nobody can find."""
        path = write_project(tmp_path, "different-name.md", VALID_PROJECT)

        with pytest.raises(ContentError, match="does not match the filename"):
            parse_project_file(path)

    def test_skips_underscore_prefixed_files(self, tmp_path: Path) -> None:
        """The template and the worked example must never reach the database."""
        write_project(tmp_path, "example-project.md", VALID_PROJECT)
        write_project(
            tmp_path, "_template.md", VALID_PROJECT.replace("example-project", "_template")
        )

        projects = load_projects(tmp_path)

        assert [project.slug for project in projects] == ["example-project"]

    def test_the_repository_content_is_valid(self) -> None:
        """The real content/ directory must always pass — this is what CI gates on."""
        content_dir = Path(__file__).resolve().parents[3] / "content"

        projects = load_projects(content_dir)

        assert isinstance(projects, list)


class TestSeeding:
    async def test_creates_documents(self, connected_app: FastAPI, tmp_path: Path) -> None:
        write_project(tmp_path, "example-project.md", VALID_PROJECT)

        result = await seed_content(tmp_path)

        assert result.created == ["example-project"]
        stored = await Project.find_one(Project.slug == "example-project")
        assert stored is not None
        assert stored.title == "Example Project"
        assert "<h2>Context</h2>" in stored.body_html

    async def test_running_twice_changes_nothing(
        self,
        connected_app: FastAPI,
        tmp_path: Path,
    ) -> None:
        """Idempotence, asserted rather than assumed."""
        write_project(tmp_path, "example-project.md", VALID_PROJECT)
        await seed_content(tmp_path)
        first = await Project.find_one(Project.slug == "example-project")
        assert first is not None

        result = await seed_content(tmp_path)

        assert result.unchanged == ["example-project"]
        second = await Project.find_one(Project.slug == "example-project")
        assert second is not None
        # updated_at stays meaningful: it tracks content changes, not deploy times.
        assert second.updated_at == first.updated_at

    async def test_updates_a_changed_project(
        self,
        connected_app: FastAPI,
        tmp_path: Path,
    ) -> None:
        write_project(tmp_path, "example-project.md", VALID_PROJECT)
        await seed_content(tmp_path)

        write_project(
            tmp_path,
            "example-project.md",
            VALID_PROJECT.replace("title: Example Project", "title: Renamed Project"),
        )
        result = await seed_content(tmp_path)

        assert result.updated == ["example-project"]
        stored = await Project.find_one(Project.slug == "example-project")
        assert stored is not None
        assert stored.title == "Renamed Project"

    async def test_never_deletes(self, connected_app: FastAPI, tmp_path: Path) -> None:
        """A file removed by accident must not wipe live content."""
        write_project(tmp_path, "example-project.md", VALID_PROJECT)
        await seed_content(tmp_path)

        (tmp_path / "projects" / "example-project.md").unlink()
        await seed_content(tmp_path)

        assert await Project.find_one(Project.slug == "example-project") is not None

    async def test_dry_run_writes_nothing(
        self,
        connected_app: FastAPI,
        tmp_path: Path,
    ) -> None:
        write_project(tmp_path, "example-project.md", VALID_PROJECT)

        result = await seed_content(tmp_path, dry_run=True)

        assert result.created == ["example-project"]
        assert await Project.find_one(Project.slug == "example-project") is None

    async def test_reports_totals(self) -> None:
        result = SeedResult(created=["a"], updated=["b", "c"], unchanged=["d"])

        assert result.total == 4


class TestCommandLine:
    """The CLI is the interface CI and the author actually use."""

    def test_check_validates_without_a_database(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        # --check must not need MongoDB: it gates content pull requests, where spinning up
        # a database to read four files would be waste.
        write_project(tmp_path, "example-project.md", VALID_PROJECT)

        exit_code = main(["--check", "--content-dir", str(tmp_path)])

        assert exit_code == 0
        assert "1 project(s) valid, 1 published" in capsys.readouterr().out

    def test_check_fails_on_invalid_content(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        write_project(tmp_path, "broken.md", "no frontmatter here")

        exit_code = main(["--check", "--content-dir", str(tmp_path)])

        assert exit_code == 1
        assert "content error" in capsys.readouterr().err

    def test_reports_a_missing_content_directory(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        exit_code = main(["--check", "--content-dir", str(tmp_path / "nowhere")])

        assert exit_code == 1
        assert "not found" in capsys.readouterr().err

    def test_defaults_to_the_repository_content_directory(self) -> None:
        args = parse_args([])

        assert args.content_dir.name == "content"
        assert args.check is False
        assert args.dry_run is False


def test_default_content_dir_points_at_the_repository_content() -> None:
    """Same failure mode as REPO_ROOT: silently resolving to a directory that does not exist."""
    assert (DEFAULT_CONTENT_DIR / "projects").is_dir()


VALID_PROFILE = """
name: Andrés M
headline: Frontend Developer
location: Manizales, Colombia
bio: >
  A short bio.
links:
  github: https://github.com/example
  linkedin: https://linkedin.com/in/example
languages:
  - name: Spanish
    level: Native
skills:
  - group: Frontend
    items: [Vue.js, TypeScript]
experience:
  - company: NICE
    role: Frontend Developer
    start: '2024-06'
    end: null
    summary: Frontend development.
    highlights: []
education:
  - institution: Universidad de Caldas
    degree: Systems and Computing Engineering
    start: '2008'
    end: '2014'
certifications: [Curso Profesional de Vue.js]
"""


def write_profile(directory: Path, body: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)

    # A content directory without projects/ is a misconfiguration the loader refuses, so
    # the fixture creates the (possibly empty) directory it expects.
    (directory / "projects").mkdir(exist_ok=True)

    path = directory / "profile.yml"
    path.write_text(body, encoding="utf-8")
    return path


class TestProfileLoader:
    def test_parses_a_valid_profile(self, tmp_path: Path) -> None:
        write_profile(tmp_path, VALID_PROFILE)

        profile = load_profile(tmp_path)

        assert profile.name == "Andrés M"
        assert profile.experience[0].company == "NICE"
        assert profile.experience[0].end is None
        assert profile.education[0].end == "2014"

    def test_email_is_optional(self, tmp_path: Path) -> None:
        """Publishing a personal address is the author's choice; the site must work either way."""
        write_profile(tmp_path, VALID_PROFILE)

        profile = load_profile(tmp_path)

        assert profile.email is None

    def test_rejects_an_unknown_field(self, tmp_path: Path) -> None:
        write_profile(tmp_path, VALID_PROFILE + "\nnickname: typo\n")

        with pytest.raises(ContentError, match="nickname"):
            load_profile(tmp_path)

    def test_rejects_a_malformed_date(self, tmp_path: Path) -> None:
        write_profile(tmp_path, VALID_PROFILE.replace("start: '2024-06'", "start: June 2024"))

        with pytest.raises(ContentError, match="start"):
            load_profile(tmp_path)

    def test_reports_a_missing_profile_file(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError, match="profile file not found"):
            load_profile(tmp_path)

    def test_the_repository_profile_is_valid(self) -> None:
        """The real content/profile.yml must always pass — CI gates on this."""
        content_dir = Path(__file__).resolve().parents[3] / "content"

        profile = load_profile(content_dir)

        assert profile.name
        assert profile.links.github


class TestProfileSeeding:
    async def test_creates_the_profile(self, connected_app: FastAPI, tmp_path: Path) -> None:
        write_profile(tmp_path, VALID_PROFILE)

        result = await seed_content(tmp_path)

        assert result.profile_written is True
        stored = await Profile.find_one(Profile.key == "profile")
        assert stored is not None
        assert stored.name == "Andrés M"
        assert len(stored.experience) == 1

    async def test_running_twice_leaves_the_profile_alone(
        self,
        connected_app: FastAPI,
        tmp_path: Path,
    ) -> None:
        write_profile(tmp_path, VALID_PROFILE)
        await seed_content(tmp_path)

        result = await seed_content(tmp_path)

        assert result.profile_written is False

    async def test_updates_a_changed_profile(
        self,
        connected_app: FastAPI,
        tmp_path: Path,
    ) -> None:
        write_profile(tmp_path, VALID_PROFILE)
        await seed_content(tmp_path)

        write_profile(
            tmp_path,
            VALID_PROFILE.replace(
                "headline: Frontend Developer", "headline: Senior Frontend Developer"
            ),
        )
        result = await seed_content(tmp_path)

        assert result.profile_written is True
        stored = await Profile.find_one(Profile.key == "profile")
        assert stored is not None
        assert stored.headline == "Senior Frontend Developer"

    async def test_dry_run_does_not_write_the_profile(
        self,
        connected_app: FastAPI,
        tmp_path: Path,
    ) -> None:
        write_profile(tmp_path, VALID_PROFILE)

        result = await seed_content(tmp_path, dry_run=True)

        assert result.profile_written is True
        assert await Profile.find_one(Profile.key == "profile") is None
