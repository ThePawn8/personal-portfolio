"""Settings validation."""

import pytest
from pydantic import ValidationError

from portfolio_api.core.config import PLACEHOLDER_SALT, get_settings
from tests.conftest import SettingsFactory

VALID_PRODUCTION = {
    "app_env": "production",
    "ip_hash_salt": "b" * 64,
    "resend_api_key": "re_test",
    "contact_to_email": "me@example.com",
    "contact_from_email": "site@example.com",
    "cors_allowed_origins": ["https://example.com"],
}


def test_defaults_are_usable_locally(build_settings: SettingsFactory) -> None:
    settings = build_settings()

    assert settings.app_env == "local"
    assert settings.is_production is False
    assert settings.mongodb_db == "portfolio"
    assert settings.contact_rate_limit_per_hour == 5


def test_cors_origins_accept_a_comma_separated_string(build_settings: SettingsFactory) -> None:
    """The natural .env spelling must work, not just JSON."""
    settings = build_settings(cors_allowed_origins="https://a.example, https://b.example")

    assert settings.cors_allowed_origins == ["https://a.example", "https://b.example"]


def test_wildcard_cors_origin_is_rejected(build_settings: SettingsFactory) -> None:
    with pytest.raises(ValidationError, match="exact origins"):
        build_settings(cors_allowed_origins=["*"])


def test_production_rejects_the_placeholder_salt(build_settings: SettingsFactory) -> None:
    """A shared salt makes the hashed IPs in the rate limiter reversible."""
    with pytest.raises(ValidationError, match="IP_HASH_SALT is still the placeholder"):
        build_settings(**{**VALID_PRODUCTION, "ip_hash_salt": PLACEHOLDER_SALT})


def test_production_rejects_a_short_salt(build_settings: SettingsFactory) -> None:
    """A short salt is brute-forceable, which is the same failure as no salt at all."""
    with pytest.raises(ValidationError, match="at least 32 characters"):
        build_settings(**{**VALID_PRODUCTION, "ip_hash_salt": "too-short"})


def test_production_requires_email_configuration(build_settings: SettingsFactory) -> None:
    """Without these, every contact message is silently dropped."""
    with pytest.raises(ValidationError) as exc_info:
        build_settings(
            app_env="production",
            ip_hash_salt="b" * 64,
            cors_allowed_origins=["https://example.com"],
        )

    message = str(exc_info.value)
    assert "RESEND_API_KEY is required" in message
    assert "CONTACT_TO_EMAIL is required" in message
    assert "CONTACT_FROM_EMAIL is required" in message


def test_production_rejects_insecure_cors_origins(build_settings: SettingsFactory) -> None:
    with pytest.raises(ValidationError, match="must use https in production"):
        build_settings(**{**VALID_PRODUCTION, "cors_allowed_origins": ["http://example.com"]})


def test_valid_production_configuration_is_accepted(build_settings: SettingsFactory) -> None:
    settings = build_settings(**VALID_PRODUCTION)

    assert settings.is_production is True


def test_get_settings_is_cached() -> None:
    get_settings.cache_clear()

    assert get_settings() is get_settings()

    get_settings.cache_clear()
