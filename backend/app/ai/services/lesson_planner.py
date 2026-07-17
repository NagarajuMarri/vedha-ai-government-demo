"""Deterministic lesson planner for Sprint 3B."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LessonPlan:
    """Deterministic planning metadata derived from the request context."""

    learner_stage: str
    explanation_depth: str
    vocabulary_complexity: str
    example_complexity: str
    max_explanation_steps: int
    notation_appropriate: bool
    encouragement_style: str


class LessonPlanner:
    """Derive deterministic teaching guidance without calling the AI provider."""

    def plan(self, *, class_level: int, subject: str, learning_profile: str, question: str) -> LessonPlan:
        """Produce a stable lesson plan for the route layer."""

        if 1 <= class_level <= 2:
            learner_stage = "early primary"
            explanation_depth = "very simple"
            vocabulary_complexity = "very easy"
            example_complexity = "single concrete picture example"
            max_explanation_steps = 3
            notation_appropriate = subject in {"Mathematics", "Science"} and len(question) < 80
            encouragement_style = "gentle encouragement"
        elif 3 <= class_level <= 5:
            learner_stage = "primary"
            explanation_depth = "simple"
            vocabulary_complexity = "easy"
            example_complexity = "short classroom example"
            max_explanation_steps = 4
            notation_appropriate = subject in {"Mathematics", "Science"} and len(question) < 120
            encouragement_style = "supportive encouragement"
        elif 6 <= class_level <= 8:
            learner_stage = "middle school"
            explanation_depth = "moderate"
            vocabulary_complexity = "medium"
            example_complexity = "guided example with one connection"
            max_explanation_steps = 5
            notation_appropriate = subject in {"Mathematics", "Science"}
            encouragement_style = "confident encouragement"
        elif 9 <= class_level <= 10:
            learner_stage = "secondary"
            explanation_depth = "deeper"
            vocabulary_complexity = "higher"
            example_complexity = "concept-linked example"
            max_explanation_steps = 6
            notation_appropriate = subject in {"Mathematics", "Science"}
            encouragement_style = "steady encouragement"
        else:
            learner_stage = "higher secondary"
            explanation_depth = "advanced"
            vocabulary_complexity = "advanced"
            example_complexity = "layered example with context"
            max_explanation_steps = 6
            notation_appropriate = subject in {"Mathematics", "Science"}
            encouragement_style = "focused encouragement"

        if learning_profile == "pure_telugu":
            vocabulary_complexity = "telugu-first academic"
            example_complexity = "natural Telugu example"

        return LessonPlan(
            learner_stage=learner_stage,
            explanation_depth=explanation_depth,
            vocabulary_complexity=vocabulary_complexity,
            example_complexity=example_complexity,
            max_explanation_steps=max_explanation_steps,
            notation_appropriate=notation_appropriate,
            encouragement_style=encouragement_style,
        )
