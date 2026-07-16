"""Provider-neutral lesson generation interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.app.ai.lesson_models import LessonGenerationRequest, LessonResult


class LessonProvider(ABC):
    """Abstract provider contract for lesson generation."""

    @abstractmethod
    def generate_lesson(self, request: LessonGenerationRequest) -> LessonResult:
        """Generate or return a typed lesson result."""
