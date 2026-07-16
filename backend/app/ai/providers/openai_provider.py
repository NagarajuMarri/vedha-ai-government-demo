"""OpenAI provider implementation for structured lesson generation."""

from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from backend.app.ai.exceptions import (
    AIAuthenticationError,
    AIConfigurationError,
    AIRateLimitError,
    AITimeoutError,
    AIProviderUnavailableError,
    AIInvalidResponseError,
)
from backend.app.ai.lesson_models import LessonGenerationRequest, LessonResult
from backend.app.ai.prompt_builder import LessonPromptBuilder
from backend.app.ai.providers.base import LessonProvider
from backend.app.core.config import Settings


class OpenAIProvider(LessonProvider):
    """OpenAI Responses API provider with schema validation."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = OpenAI(
            api_key=settings.openai_api_key,
            timeout=settings.openai_timeout_seconds,
        ) if settings.openai_api_key else None

    def generate_lesson(self, request: LessonGenerationRequest) -> LessonResult:
        """Generate a lesson using the OpenAI Responses API and validate the output."""

        if not self._settings.openai_api_key:
            raise AIConfigurationError("OPENAI_API_KEY is not configured")

        prompt = LessonPromptBuilder().build(
            class_level=request.class_level,
            subject=request.subject,
            learning_profile=request.learning_profile,
            student_question=request.student_question,
        )

        try:
            response = self._client.responses.create(
                model=self._settings.openai_model,
                input=prompt,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "lesson_result",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "introduction": {"type": "string"},
                                "explanation_steps": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "minItems": 1,
                                },
                                "example": {"type": "string"},
                                "key_points": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "minItems": 1,
                                },
                                "check_question": {"type": "string"},
                                "learning_profile": {"type": "string"},
                                "subject": {"type": "string"},
                                "class_level": {"type": "string"},
                                "source": {"type": "string"},
                                "fallback_used": {"type": "boolean"},
                            },
                            "required": [
                                "title",
                                "introduction",
                                "explanation_steps",
                                "example",
                                "key_points",
                                "check_question",
                                "learning_profile",
                                "subject",
                                "class_level",
                                "source",
                                "fallback_used",
                            ],
                        },
                    },
                },
            )
        except Exception as exc:  # noqa: BLE001
            error_text = f"{type(exc).__name__} {str(exc)}".lower()
            if "auth" in error_text or "authentication" in error_text or "api key" in error_text or "key" in error_text:
                raise AIAuthenticationError("Provider authentication failed") from exc
            if "rate limit" in error_text or "too many requests" in error_text or "ratelimit" in error_text:
                raise AIRateLimitError("Provider rate limit exceeded") from exc
            if "timeout" in error_text:
                raise AITimeoutError("Provider request timed out") from exc
            if "unavailable" in error_text or "connection" in error_text or "service" in error_text:
                raise AIProviderUnavailableError("Provider service is unavailable") from exc
            raise AIProviderUnavailableError("Provider request failed") from exc

        raw_text = getattr(response, "output_text", None)
        if not raw_text:
            raise AIInvalidResponseError("Provider returned an empty response")

        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise AIInvalidResponseError("Provider returned invalid JSON") from exc

        try:
            return LessonResult.model_validate(parsed)
        except Exception as exc:  # noqa: BLE001
            raise AIInvalidResponseError("Provider output failed schema validation") from exc
