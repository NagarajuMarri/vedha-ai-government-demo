"""Internal lesson-generation service for future Sprint 3B route integration."""

from __future__ import annotations

from backend.app.ai.exceptions import AIConfigurationError, AIInfrastructureError
from backend.app.ai.fallback_generator import DeterministicFallbackLessonGenerator
from backend.app.ai.language_profiles import get_language_profile
from backend.app.ai.lesson_models import LessonGenerationRequest, LessonResult
from backend.app.ai.prompt_builder import LessonPromptBuilder
from backend.app.ai.providers.base import LessonProvider
from backend.app.core.config import Settings


class LessonGenerationService:
    """Orchestrates provider selection, prompt construction, and fallback handling."""

    def __init__(self, settings: Settings, provider: LessonProvider | None = None) -> None:
        self._settings = settings
        self._provider = provider
        self._fallback_generator = DeterministicFallbackLessonGenerator()
        self._prompt_builder = LessonPromptBuilder()

    def generate_lesson(self, request: LessonGenerationRequest) -> LessonResult:
        """Generate a typed lesson result using provider or approved fallback."""

        get_language_profile(request.learning_profile)

        if self._settings.ai_fallback_enabled is False and self._provider is None:
            raise AIConfigurationError("AI fallback disabled and no provider configured")

        prompt = self._prompt_builder.build(
            class_level=request.class_level,
            subject=request.subject,
            learning_profile=request.learning_profile,
            student_question=request.student_question,
        )

        provider = self._provider
        if provider is None:
            return self._fallback_generator.generate(request)

        try:
            result = provider.generate_lesson(request)
            return result
        except AIInfrastructureError:
            if self._settings.ai_fallback_enabled:
                return self._fallback_generator.generate(request)
            raise

        return self._fallback_generator.generate(request)
