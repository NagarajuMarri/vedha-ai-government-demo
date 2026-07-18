"""OpenAI Responses API provider with strict structured parsing."""

from __future__ import annotations

from typing import Any

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    OpenAI,
    RateLimitError,
)

from backend.app.ai.exceptions import (
    AIAuthenticationError,
    AIConfigurationError,
    AIInsufficientQuotaError,
    AIInvalidResponseError,
    AIModelNotFoundError,
    AIProviderUnavailableError,
    AIRateLimitError,
    AIRefusalError,
    AITimeoutError,
)
from backend.app.ai.lesson_models import GeneratedLessonContent, LessonGenerationRequest, LessonResult
from backend.app.ai.prompt_builder import LessonPromptBuilder
from backend.app.ai.providers.base import LessonProvider
from backend.app.core.config import Settings


class OpenAIProvider(LessonProvider):
    """Generate lessons with the official SDK and application-owned metadata."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = None
        if settings.openai_api_key:
            self._client = OpenAI(
                api_key=settings.openai_api_key,
                timeout=settings.openai_timeout_seconds,
            )

    def generate_lesson(self, request: LessonGenerationRequest) -> LessonResult:
        """Generate and strictly parse one lesson using the Responses API."""

        if not self._settings.openai_api_key:
            raise AIConfigurationError("OPENAI_API_KEY is not configured")
        if not self._settings.openai_model:
            raise AIConfigurationError("OPENAI_MODEL is not configured")
        if not self._settings.openai_timeout_seconds:
            raise AIConfigurationError("OPENAI_TIMEOUT_SECONDS is not configured")

        prompt = LessonPromptBuilder().build_request(
            class_level=request.class_level,
            subject=request.subject,
            learning_profile=request.learning_profile,
            student_question=request.student_question,
            concept=request.concept,
        )

        try:
            response = self._client.responses.parse(
                model=self._settings.openai_model,
                instructions=prompt.instructions,
                input=prompt.student_input,
                text_format=GeneratedLessonContent,
                store=False,
            )
        except AuthenticationError as exc:
            raise AIAuthenticationError("Provider authentication failed") from exc
        except RateLimitError as exc:
            if self._provider_error_code(exc) == "insufficient_quota":
                raise AIInsufficientQuotaError("Provider quota is insufficient") from exc
            raise AIRateLimitError("Provider rate limit exceeded") from exc
        except APITimeoutError as exc:
            raise AITimeoutError("Provider request timed out") from exc
        except APIConnectionError as exc:
            raise AIProviderUnavailableError("Provider connection failed") from exc
        except BadRequestError as exc:
            if self._provider_error_code(exc) == "model_not_found":
                raise AIModelNotFoundError("Configured model is unavailable") from exc
            raise AIProviderUnavailableError("Provider rejected the configured request") from exc
        except APIStatusError as exc:
            if self._provider_error_code(exc) == "model_not_found" or getattr(exc, "status_code", None) == 404:
                raise AIModelNotFoundError("Configured model is unavailable") from exc
            raise AIProviderUnavailableError("Provider service request failed") from exc
        except Exception as exc:  # SDK parsing/Pydantic errors are not public
            error_name = type(exc).__name__.lower()
            if "authentication" in error_name:
                raise AIAuthenticationError("Provider authentication failed") from exc
            if "ratelimit" in error_name or "rate_limit" in error_name:
                raise AIRateLimitError("Provider rate limit exceeded") from exc
            if "timeout" in error_name:
                raise AITimeoutError("Provider request timed out") from exc
            if "unavailable" in error_name or "connection" in error_name:
                raise AIProviderUnavailableError("Provider service is unavailable") from exc
            raise AIInvalidResponseError("Provider output could not be parsed") from exc

        parsed = getattr(response, "output_parsed", None)
        if parsed is None:
            if self._contains_refusal(response):
                raise AIRefusalError("Provider refused the lesson request")
            raise AIInvalidResponseError("Provider returned no structured lesson")
        if not isinstance(parsed, GeneratedLessonContent):
            try:
                parsed = GeneratedLessonContent.model_validate(parsed)
            except Exception as exc:
                raise AIInvalidResponseError("Provider output failed schema validation") from exc

        content = parsed.model_dump(
            exclude={"subject", "class_level", "learning_profile"},
        )
        return LessonResult(
            **content,
            subject=request.subject,
            class_level=request.class_level,
            learning_profile=request.learning_profile,
            source="openai",
            fallback_used=False,
            prompt_id=prompt.prompt_id,
            prompt_version=prompt.prompt_version,
        )

    @staticmethod
    def _contains_refusal(response: Any) -> bool:
        """Detect SDK refusal content without exposing its provider text."""

        for output in getattr(response, "output", ()) or ():
            for content in getattr(output, "content", ()) or ():
                if getattr(content, "type", None) == "refusal" or getattr(content, "refusal", None):
                    return True
        return False

    @staticmethod
    def _provider_error_code(exception: Exception) -> str | None:
        """Extract only a provider error code; never expose the raw response."""

        direct_code = getattr(exception, "code", None)
        if isinstance(direct_code, str):
            return direct_code
        body = getattr(exception, "body", None)
        if isinstance(body, dict):
            error = body.get("error", body)
            if isinstance(error, dict) and isinstance(error.get("code"), str):
                return error["code"]
        return None
