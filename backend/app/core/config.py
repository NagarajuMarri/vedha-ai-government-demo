"""Environment-backed application settings."""

from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def _read_csv(name: str, default: str) -> tuple[str, ...]:
    """Read a comma-separated environment setting into non-empty values."""

    raw_value = os.getenv(name, default)
    values = tuple(value.strip() for value in raw_value.split(",") if value.strip())
    if not values:
        raise ValueError(f"{name} must contain at least one value")
    return values


def _read_bool(name: str, default: bool) -> bool:
    """Read a boolean environment setting."""

    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    normalized = raw_value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} must be a boolean value")


def _read_timeout_seconds(name: str, default: int) -> int:
    """Read and validate a timeout environment setting."""

    raw_value = os.getenv(name, str(default))
    try:
        timeout = int(raw_value.strip())
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer number of seconds") from exc
    if timeout <= 0:
        raise ValueError(f"{name} must be greater than zero")
    return timeout


@dataclass(frozen=True, slots=True)
class Settings:
    """Validated process settings loaded from environment variables."""

    project_name: str
    environment: str
    api_v1_prefix: str
    log_level: str
    cors_origins: tuple[str, ...]
    openai_api_key: str | None
    openai_model: str
    openai_timeout_seconds: int
    ai_provider: str
    ai_fallback_enabled: bool


@lru_cache
def get_settings() -> Settings:
    """Load and cache settings for the lifetime of the process."""

    project_name = os.getenv("VEDHA_PROJECT_NAME", "Vedha AI Government Demo").strip()
    environment = os.getenv("VEDHA_ENVIRONMENT", "development").strip().lower()
    api_v1_prefix = os.getenv("VEDHA_API_V1_PREFIX", "/api/v1").strip()
    log_level = os.getenv("VEDHA_LOG_LEVEL", "INFO").strip().upper()
    openai_api_key = os.getenv("OPENAI_API_KEY", "").strip() or None
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    openai_timeout_seconds = _read_timeout_seconds("OPENAI_TIMEOUT_SECONDS", 20)
    ai_provider = os.getenv("AI_PROVIDER", "openai").strip().lower()
    ai_fallback_enabled = _read_bool("AI_FALLBACK_ENABLED", True)

    if not project_name:
        raise ValueError("VEDHA_PROJECT_NAME must not be empty")
    if environment not in {"development", "test", "staging", "production"}:
        raise ValueError("VEDHA_ENVIRONMENT has an unsupported value")
    if not api_v1_prefix.startswith("/") or api_v1_prefix.endswith("/"):
        raise ValueError("VEDHA_API_V1_PREFIX must start with '/' and not end with '/'")
    if log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ValueError("VEDHA_LOG_LEVEL has an unsupported value")
    if ai_provider not in {"openai", "fallback"}:
        raise ValueError("AI_PROVIDER must be 'openai' or 'fallback'")

    return Settings(
        project_name=project_name,
        environment=environment,
        api_v1_prefix=api_v1_prefix,
        log_level=log_level,
        cors_origins=_read_csv(
            "VEDHA_CORS_ORIGINS",
            "http://localhost:8080,http://127.0.0.1:8080",
        ),
        openai_api_key=openai_api_key,
        openai_model=openai_model,
        openai_timeout_seconds=openai_timeout_seconds,
        ai_provider=ai_provider,
        ai_fallback_enabled=ai_fallback_enabled,
    )
