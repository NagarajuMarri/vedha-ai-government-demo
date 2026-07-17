"""Provider-neutral lesson generation orchestration."""

from __future__ import annotations

from backend.app.ai.exceptions import AIInfrastructureError, AIReviewerRejectionError
from backend.app.ai.fallback_generator import DeterministicFallbackLessonGenerator
from backend.app.ai.language_profiles import get_language_profile
from backend.app.ai.lesson_models import LessonGenerationRequest, LessonResult
from backend.app.ai.providers.base import LessonProvider
from backend.app.ai.providers.openai_provider import OpenAIProvider
from backend.app.ai.services.lesson_reviewer import LessonReviewer
from backend.app.core.config import Settings


class LessonGenerationService:
    """Select a provider, review its result, and apply approved fallback."""

    def __init__(self, settings: Settings, provider: LessonProvider | None = None) -> None:
        self._settings = settings
        self._provider = provider or self._configured_provider()
        self._fallback_generator = DeterministicFallbackLessonGenerator()
        self._reviewer = LessonReviewer()
        self.last_fallback_reason: str | None = None
        self.last_validation_rule: str | None = None

    def _configured_provider(self) -> LessonProvider | None:
        if self._settings.ai_provider == "openai":
            return OpenAIProvider(self._settings)
        return None

    def generate_lesson(self, request: LessonGenerationRequest) -> LessonResult:
        """Return reviewed provider output or a reviewed deterministic fallback."""

        get_language_profile(request.learning_profile)
        if self._provider is not None:
            try:
                provider_lesson = self._provider.generate_lesson(request)
            except AIInfrastructureError as exc:
                self.last_fallback_reason = exc.category
                if not self._settings.ai_fallback_enabled:
                    raise
            else:
                try:
                    return self._reviewer.review(provider_lesson, request)
                except AIReviewerRejectionError as exc:
                    self.last_fallback_reason = "reviewer_rejection"
                    self.last_validation_rule = exc.validation_rule
                    if not self._settings.ai_fallback_enabled:
                        raise
        elif not self._settings.ai_fallback_enabled:
            from backend.app.ai.exceptions import AIConfigurationError
            raise AIConfigurationError("Fallback is disabled and no provider is configured")
        elif self._settings.ai_provider == "fallback":
            self.last_fallback_reason = "missing_configuration"

        return self._reviewer.review(self._fallback_generator.generate(request), request)
