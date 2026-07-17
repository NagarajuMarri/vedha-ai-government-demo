"""Central logging configuration."""

import logging
from logging.config import dictConfig


def configure_logging(level: str) -> None:
    """Configure concise process-wide console logging."""

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": (
                        "%(asctime)s %(levelname)s %(name)s %(message)s "
                        "request_id=%(request_id)s lesson_id=%(lesson_id)s "
                        "provider=%(provider)s model=%(model)s prompt_id=%(prompt_id)s "
                        "prompt_version=%(prompt_version)s outcome=%(outcome)s "
                        "fallback_reason=%(fallback_reason)s latency_ms=%(latency_ms)s "
                        "error_category=%(error_category)s failed_validation_rule=%(failed_validation_rule)s"
                    ),
                    "defaults": {
                        "request_id": "-",
                        "lesson_id": "-",
                        "provider": "-",
                        "model": "-",
                        "prompt_id": "-",
                        "prompt_version": "-",
                        "outcome": "-",
                        "fallback_reason": "-",
                        "latency_ms": "-",
                        "error_category": "-",
                        "failed_validation_rule": "-",
                    },
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                }
            },
            "root": {"handlers": ["console"], "level": level},
        }
    )
    logging.getLogger(__name__).info("Logging configured", extra={"log_level": level})
