"""Deterministic prompt builder for lesson generation."""

from __future__ import annotations

from backend.app.ai.language_profiles import get_language_profile


class LessonPromptBuilder:
    """Create provider-neutral prompt text for lesson generation."""

    def build(
        self,
        *,
        class_level: str,
        subject: str,
        learning_profile: str,
        student_question: str,
    ) -> str:
        """Assemble a deterministic, testable prompt body."""

        profile = get_language_profile(learning_profile)
        instructions = "\n".join(profile.concise_prompt_instructions)
        forbidden = "\n".join(profile.forbidden_behaviour)

        return (
            f"You are helping a Class {class_level} student studying {subject}.\n"
            f"The selected learning profile is {learning_profile}.\n"
            f"Language policy:\n{instructions}\n"
            f"Teaching requirements:\n"
            "- Teach the concept before testing.\n"
            "- Use age-appropriate explanation.\n"
            "- Show step-by-step reasoning.\n"
            "- Include one simple example.\n"
            "- Encourage the learner.\n"
            "- End with one understanding-check question.\n"
            "- Do not generate any practice set in this sprint.\n"
            f"Forbidden behaviour:\n{forbidden}\n"
            "Structured output requirements:\n"
            "- Return a structured lesson result that matches the approved lesson schema.\n"
            "- The result must include a title, introduction, explanation_steps, example, key_points, check_question, learning_profile, subject, class_level, source, and fallback_used.\n"
            "- Ensure the explanation_steps list is non-empty and ordered.\n"
            "- Ensure the key_points list is non-empty.\n"
            f"Student question: {student_question}"
        )
