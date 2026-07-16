"""Deterministic fallback lesson generator for approved recoverable failures."""

from __future__ import annotations

from backend.app.ai.lesson_models import LessonGenerationRequest, LessonResult


class DeterministicFallbackLessonGenerator:
    """Provide safe, provider-independent fallback lesson content."""

    def generate(self, request: LessonGenerationRequest) -> LessonResult:
        """Create deterministic fallback output from the normalized request."""

        profile = request.learning_profile
        explanation = self._build_explanation(profile, request.subject)

        return LessonResult(
            title=f"{request.subject} foundation for Class {request.class_level}",
            introduction=(
                f"This fallback lesson explains the idea behind {request.subject} in a clear, "
                f"age-appropriate way so you can continue learning without a live provider response."
            ),
            explanation_steps=[
                "Start with the key idea in simple language.",
                explanation,
                "Review the idea with one small example and a short check.",
            ],
            example=f"Try a simple example related to {request.subject} and connect it to {request.student_question}.",
            key_points=[
                "Learn the core idea first.",
                "Use a simple example to connect the idea to the question.",
                "Check your understanding with the final question.",
            ],
            check_question=f"Can you explain the main idea of {request.subject} in your own words?",
            learning_profile=profile,
            subject=request.subject,
            class_level=request.class_level,
            source="fallback",
            fallback_used=True,
        )

    def _build_explanation(self, profile: str, subject: str) -> str:
        if profile == "english_medium":
            return f"In English medium, focus on the main concept in {subject} and explain it in clear, simple steps."
        if profile == "telugu_assisted_english":
            return f"In Telugu-assisted English, explain the core idea of {subject} mainly in Telugu while keeping important technical terms clear."
        return f"In pure Telugu, explain the main idea of {subject} naturally in Telugu, using academic words where they help understanding."
