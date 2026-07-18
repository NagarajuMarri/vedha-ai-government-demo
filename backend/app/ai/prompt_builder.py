"""Deterministic, versioned prompt builder for lesson generation."""

from __future__ import annotations

from dataclasses import dataclass

from backend.app.ai.language_profiles import (
    PURE_TELUGU_MATHEMATICS_TERMS,
    get_language_profile,
    localize_subject,
)
from backend.app.ai.prompt_registry import PromptDefinition, get_active_prompt


@dataclass(frozen=True, slots=True)
class BuiltLessonPrompt:
    """Trusted instructions and untrusted learner input kept separate."""

    prompt_id: str
    prompt_version: str
    instructions: str
    student_input: str


class LessonPromptBuilder:
    """Create provider-neutral prompts from governed policy definitions."""

    def build_request(
        self,
        *,
        class_level: str,
        subject: str,
        learning_profile: str,
        student_question: str,
        concept: str = "General",
    ) -> BuiltLessonPrompt:
        """Build a versioned prompt while isolating untrusted question text."""

        profile = get_language_profile(learning_profile)
        definition = get_active_prompt(subject, learning_profile)
        localized_subject = localize_subject(subject, learning_profile)
        language_rules = "\n".join(f"- {item}" for item in profile.concise_prompt_instructions)
        subject_rules = "\n".join(f"- {item}" for item in definition.teaching_rules)
        terminology = ""
        if subject == "Mathematics" and learning_profile == "pure_telugu":
            terminology = "\nApproved context-aware terminology:\n" + "\n".join(
                f"- {english}: {telugu}" for english, telugu in PURE_TELUGU_MATHEMATICS_TERMS.items()
            )
        scope_rules = self._elementary_scope_rules(
            class_level=class_level,
            subject=subject,
            student_question=student_question,
        )
        social_studies_rules = ""
        if subject == "Social Studies":
            social_studies_rules = (
                "\nSocial Studies concept rules:\n"
                "- Identify whether the selected concept is history, geography, or civics and teach that exact branch.\n"
                "- Anchor the explanation in relevant people, places, institutions, dates, physical features, evidence, and cause-and-effect as appropriate.\n"
                "- Include a concrete India or Andhra Pradesh connection when factually relevant.\n"
                "- Never answer with generic study advice or a broad description of Social Studies.\n"
                "- For pure_telugu, translate the concept naturally and keep every learner-facing sentence in Telugu."
            )

        instructions = (
            f"Prompt ID: {definition.prompt_id}\n"
            f"Prompt version: {definition.prompt_version}\n"
            f"Teach a Class {class_level} lesson for subject {subject}.\n"
            f"The learner-facing subject name for this profile is {localized_subject}.\n"
            f"The selected learning profile is {learning_profile}.\n"
            f"The required lesson concept is: {concept}.\n"
            "Concept alignment is mandatory: every section must directly teach the required lesson concept. "
            "Use the concept name or its natural translation in the title, introduction, explanation, example, key points, and check question. "
            "Do not replace the requested concept with a broad subject overview, a generic foundation lesson, or unrelated content. "
            "If the learner asks to start from scratch, define this exact concept and its essential parts before the example. "
            "Return plain readable Unicode text only. Never emit [OBJ], object-replacement characters, embedded objects, emoji placeholders, or corrupted glyph sequences.\n"
            f"Language policy:\n{language_rules}\n"
            f"Subject and teaching rules:\n{subject_rules}{terminology}{scope_rules}{social_studies_rules}\n"
            "Return only the requested Structured Output educational content. "
            "Do not return request IDs, lesson IDs, timestamps, source metadata, provider details, "
            "prompt text, chain-of-thought, or hidden reasoning. "
            "The content must include title, introduction, explanation_steps, example, key_points, "
            "check_question, learning_profile, subject, and class_level."
        )
        return BuiltLessonPrompt(
            prompt_id=definition.prompt_id,
            prompt_version=definition.prompt_version,
            instructions=instructions,
            student_input=(
                f"Selected concept (trusted application context): {concept}\n"
                f"Student question (untrusted learner text):\n{student_question}"
            ),
        )

    def build(self, **kwargs: str) -> str:
        """Return a combined representation for diagnostics and legacy tests."""

        prompt = self.build_request(**kwargs)
        return f"{prompt.instructions}\n{prompt.student_input}"

    @staticmethod
    def _elementary_scope_rules(*, class_level: str, subject: str, student_question: str) -> str:
        """Add bounded elementary guidance without rewriting learner text."""

        if not class_level.isdigit() or int(class_level) > 5 or subject != "Mathematics":
            return ""
        question = student_question.casefold()
        if "fraction" not in question and "భిన్న" not in question:
            return "\nElementary scope: use at most four short explanation steps."
        advanced_terms = (
            "lcm", "hcf", "gcf", "improper", "mixed number", "addition", "subtraction",
            "కనిష్ఠ సామాన్య గుణిజం", "గరిష్ఠ సామాన్య కారణాంకం", "అపక్రమ", "మిశ్ర సంఖ్య",
            "కూడిక", "తీసివేత",
        )
        advanced_requested = any(term in question for term in advanced_terms)
        if advanced_requested:
            return "\nElementary scope: use at most four short steps and cover only advanced topics explicitly requested."
        return (
            "\nElementary fraction scope:\n"
            "- Use at most four short explanation steps.\n"
            "- Cover only the fraction definition, numerator, denominator, one or two simple examples, key points, and one check question.\n"
            "- Do not introduce LCM, HCF/GCF, simplification, fraction operations, improper fractions, mixed numbers, or advanced classification."
        )
