"""Application settings.

The only module that reads the environment. Everything else receives a `Settings`
instance, which keeps configuration testable and makes the full set of inputs greppable
in one place.

Settings are validated at import of the first `get_settings()` call, so a misconfigured
deployment fails at boot with a precise message instead of raising a 500 on the first
request that happens to need the missing value.
"""

from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal, Self

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

# One .env at the repository root feeds both applications (see README).
# core/config.py -> portfolio_api -> src -> api -> apps -> repository root.
REPO_ROOT = Path(__file__).resolve().parents[5]

PLACEHOLDER_SALT = "change-me-to-a-random-64-char-hex-string"
MIN_SALT_LENGTH = 32

Environment = Literal["local", "preview", "production"]


class Settings(BaseSettings):
    """Runtime configuration, read from the environment or a root `.env` file."""

    model_config = SettingsConfigDict(
        env_file=REPO_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: Environment = "local"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "portfolio"

    # `NoDecode` stops pydantic-settings from JSON-parsing the value before the validator
    # below sees it. Without it, the natural `.env` spelling `A,B` raises a parse error at
    # source level and the validator never runs.
    cors_allowed_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:5173"]
    )

    resend_api_key: str = ""
    contact_to_email: str = ""
    contact_from_email: str = ""
    contact_rate_limit_per_hour: int = Field(default=5, ge=1, le=100)

    ip_hash_salt: str = PLACEHOLDER_SALT

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def split_comma_separated(cls, value: object) -> object:
        """Accept `a,b` from the environment.

        pydantic-settings parses list fields as JSON, which makes the natural
        `CORS_ALLOWED_ORIGINS=https://a.com,https://b.com` fail. Splitting here keeps
        `.env` readable.
        """
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("cors_allowed_origins")
    @classmethod
    def reject_wildcard_origin(cls, value: list[str]) -> list[str]:
        """A wildcard origin plus credentials is the classic CORS mistake — refuse it."""
        if "*" in value:
            message = "cors_allowed_origins must list exact origins; '*' is not allowed"
            raise ValueError(message)
        return value

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @model_validator(mode="after")
    def enforce_production_requirements(self) -> Self:
        """Refuse to start a production process that is missing a required secret.

        Each of these has a harmless-looking default so local development stays a
        one-command affair. In production the same default is a security bug: a shared
        salt makes hashed IPs reversible, and an unset Resend key silently drops every
        contact message. Failing at boot is the only way that gets noticed.
        """
        if not self.is_production:
            return self

        problems: list[str] = []
        if self.ip_hash_salt == PLACEHOLDER_SALT:
            problems.append("IP_HASH_SALT is still the placeholder value")
        if len(self.ip_hash_salt) < MIN_SALT_LENGTH:
            problems.append(f"IP_HASH_SALT must be at least {MIN_SALT_LENGTH} characters")
        if not self.resend_api_key:
            problems.append("RESEND_API_KEY is required in production")
        if not self.contact_to_email:
            problems.append("CONTACT_TO_EMAIL is required in production")
        if not self.contact_from_email:
            problems.append("CONTACT_FROM_EMAIL is required in production")
        if any(origin.startswith("http://") for origin in self.cors_allowed_origins):
            problems.append("CORS_ALLOWED_ORIGINS must use https in production")

        if problems:
            details = "\n  - ".join(problems)
            message = f"invalid production configuration:\n  - {details}"
            raise ValueError(message)

        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide settings, built once.

    Cached because reading and validating the environment on every request is waste, and
    because a single instance means one source of truth. Tests clear the cache or build
    `Settings(...)` directly with overrides.
    """
    return Settings()
