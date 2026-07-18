"""Environment-backed application settings."""

from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path
import re

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


def _read_timeout_seconds(name: str) -> int | None:
    """Read and validate a timeout environment setting."""

    raw_value = os.getenv(name, "").strip()
    if not raw_value:
        return None
    try:
        timeout = int(raw_value)
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
    openai_model: str | None
    openai_timeout_seconds: int | None
    ai_provider: str
    ai_fallback_enabled: bool
    supported_boards: tuple[str, ...] = (
        "andhra_pradesh_state_board",
        "telangana_state_board",
        "cbse",
        "icse",
    )
    default_board: str = "andhra_pradesh_state_board"
    default_academic_year: str = "2025-2026"
    default_curriculum_version: str | None = None
    textbook_storage_path: Path = Path(__file__).resolve().parents[2] / "data" / "textbooks"
    textbook_max_file_size_mb: int = 100
    textbook_allowed_mime_types: tuple[str, ...] = ("application/pdf",)
    textbook_checksum_algorithm: str = "sha256"
    textbook_ingestion_enabled: bool = False
    textbook_scanned_threshold: float = 0.8


@lru_cache
def get_settings() -> Settings:
    """Load and cache settings for the lifetime of the process."""

    project_name = os.getenv("VEDHA_PROJECT_NAME", "Vedha AI Government Demo").strip()
    environment = os.getenv("VEDHA_ENVIRONMENT", "development").strip().lower()
    api_v1_prefix = os.getenv("VEDHA_API_V1_PREFIX", "/api/v1").strip()
    log_level = os.getenv("VEDHA_LOG_LEVEL", "INFO").strip().upper()
    openai_api_key = os.getenv("OPENAI_API_KEY", "").strip() or None
    openai_model = os.getenv("OPENAI_MODEL", "").strip() or None
    openai_timeout_seconds = _read_timeout_seconds("OPENAI_TIMEOUT_SECONDS")
    ai_provider = os.getenv("AI_PROVIDER", "openai").strip().lower()
    ai_fallback_enabled = _read_bool("AI_FALLBACK_ENABLED", True)
    supported_boards = _read_csv(
        "SUPPORTED_BOARDS",
        "andhra_pradesh_state_board,telangana_state_board,cbse,icse",
    )
    default_board = os.getenv("DEFAULT_BOARD", "andhra_pradesh_state_board").strip()
    default_academic_year = os.getenv("DEFAULT_ACADEMIC_YEAR", "2025-2026").strip()
    default_curriculum_version = os.getenv("DEFAULT_CURRICULUM_VERSION", "").strip() or None
    textbook_storage_path = Path(os.getenv(
        "TEXTBOOK_STORAGE_PATH",
        str(Path(__file__).resolve().parents[2] / "data" / "textbooks"),
    )).resolve()
    try:
        textbook_max_file_size_mb = int(os.getenv("TEXTBOOK_MAX_FILE_SIZE_MB", "100"))
        textbook_scanned_threshold = float(os.getenv("TEXTBOOK_SCANNED_THRESHOLD", "0.8"))
    except ValueError as exc:
        raise ValueError("Textbook numeric configuration is invalid") from exc
    textbook_allowed_mime_types = _read_csv("TEXTBOOK_ALLOWED_MIME_TYPES", "application/pdf")
    textbook_checksum_algorithm = os.getenv("TEXTBOOK_CHECKSUM_ALGORITHM", "sha256").strip().lower()
    textbook_ingestion_enabled = _read_bool("TEXTBOOK_INGESTION_ENABLED", False)

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
    if default_board not in supported_boards:
        raise ValueError("DEFAULT_BOARD must be included in SUPPORTED_BOARDS")
    if not default_academic_year or not re.fullmatch(r"\d{4}-\d{4}", default_academic_year):
        raise ValueError("DEFAULT_ACADEMIC_YEAR must use YYYY-YYYY format")
    if textbook_max_file_size_mb <= 0:
        raise ValueError("TEXTBOOK_MAX_FILE_SIZE_MB must be greater than zero")
    if textbook_allowed_mime_types != ("application/pdf",):
        raise ValueError("TEXTBOOK_ALLOWED_MIME_TYPES currently supports only application/pdf")
    if textbook_checksum_algorithm != "sha256":
        raise ValueError("TEXTBOOK_CHECKSUM_ALGORITHM currently supports only sha256")
    if not 0 <= textbook_scanned_threshold <= 1:
        raise ValueError("TEXTBOOK_SCANNED_THRESHOLD must be between zero and one")

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
        supported_boards=supported_boards,
        default_board=default_board,
        default_academic_year=default_academic_year,
        default_curriculum_version=default_curriculum_version,
        textbook_storage_path=textbook_storage_path,
        textbook_max_file_size_mb=textbook_max_file_size_mb,
        textbook_allowed_mime_types=textbook_allowed_mime_types,
        textbook_checksum_algorithm=textbook_checksum_algorithm,
        textbook_ingestion_enabled=textbook_ingestion_enabled,
        textbook_scanned_threshold=textbook_scanned_threshold,
    )


def get_safe_ai_configuration(settings: Settings | None = None) -> dict[str, str | bool | None]:
    """Return non-secret AI configuration fields suitable for diagnostics."""

    resolved = settings or get_settings()
    return {
        "provider": resolved.ai_provider,
        "model": resolved.openai_model,
        "key_configured": bool(resolved.openai_api_key),
        "fallback_enabled": resolved.ai_fallback_enabled,
    }
