"""Review and normalize a generated lesson for Sprint 3B."""

from __future__ import annotations

from backend.app.ai.lesson_models import LessonResult


class LessonReviewer:
    """Perform deterministic review of a lesson response before returning it."""

    def review(self, lesson: LessonResult) -> LessonResult:
        """Normalize the lesson payload and ensure the response contract is safe."""

        cleaned = LessonResult(
            title=lesson.title.strip() or "Lesson",
            introduction=lesson.introduction.strip() or "This lesson will help you learn the topic step by step.",
            explanation_steps=[step.strip() for step in lesson.explanation_steps if step and step.strip()],
            example=lesson.example.strip() or "Try a small example to practice the idea.",
            key_points=[point.strip() for point in lesson.key_points if point and point.strip()],
            check_question=lesson.check_question.strip() or "Can you explain the idea in your own words?",
            learning_profile=lesson.learning_profile,
            subject=lesson.subject,
            class_level=lesson.class_level,
            source=lesson.source,
            fallback_used=lesson.fallback_used,
        )
        if not cleaned.explanation_steps:
            cleaned.explanation_steps = ["Start with the core idea, then build a small example."]
        if not cleaned.key_points:
            cleaned.key_points = ["Review the main idea carefully."]
        return cleaned
