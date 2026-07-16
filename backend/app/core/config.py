"""Environment-backed application settings."""

from dataclasses import dataclass
from functools import lru_cache
import os


def _read_csv(name: str, default: str) -> tuple[str, ...]:
    """Read a comma-separated environment setting into non-empty values."""

    raw_value = os.getenv(name, default)
    values = tuple(value.strip() for value in raw_value.split(",") if value.strip())
    if not values:
        raise ValueError(f"{name} must contain at least one value")
    return values


@dataclass(frozen=True, slots=True)
class Settings:
    """Validated process settings loaded from environment variables."""

    project_name: str
    environment: str
    api_v1_prefix: str
    log_level: str
    cors_origins: tuple[str, ...]


@lru_cache
def get_settings() -> Settings:
    """Load and cache settings for the lifetime of the process."""

    project_name = os.getenv("VEDHA_PROJECT_NAME", "Vedha AI Government Demo").strip()
    environment = os.getenv("VEDHA_ENVIRONMENT", "development").strip().lower()
    api_v1_prefix = os.getenv("VEDHA_API_V1_PREFIX", "/api/v1").strip()
    log_level = os.getenv("VEDHA_LOG_LEVEL", "INFO").strip().upper()

    if not project_name:
        raise ValueError("VEDHA_PROJECT_NAME must not be empty")
    if environment not in {"development", "test", "staging", "production"}:
        raise ValueError("VEDHA_ENVIRONMENT has an unsupported value")
    if not api_v1_prefix.startswith("/") or api_v1_prefix.endswith("/"):
        raise ValueError("VEDHA_API_V1_PREFIX must start with '/' and not end with '/'")
    if log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ValueError("VEDHA_LOG_LEVEL has an unsupported value")

    return Settings(
        project_name=project_name,
        environment=environment,
        api_v1_prefix=api_v1_prefix,
        log_level=log_level,
        cors_origins=_read_csv(
            "VEDHA_CORS_ORIGINS",
            "http://localhost:8080,http://127.0.0.1:8080",
        ),
    )
