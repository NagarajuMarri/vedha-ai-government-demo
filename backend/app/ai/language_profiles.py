"""Provider-independent language profile policy registry."""

from __future__ import annotations

from dataclasses import dataclass

from backend.app.ai.exceptions import AIConfigurationError


LANGUAGE_PROFILE_IDS = {
    "english_medium",
    "telugu_assisted_english",
    "pure_telugu",
}


@dataclass(frozen=True, slots=True)
class LanguageProfilePolicy:
    """Structured policy metadata for a language profile."""

    explanation_language: str
    terminology_language: str
    teaching_style: str
    example_style: str
    encouragement_style: str
    forbidden_behaviour: tuple[str, ...]
    concise_prompt_instructions: tuple[str, ...]


_LANGUAGE_PROFILES: dict[str, LanguageProfilePolicy] = {
    "english_medium": LanguageProfilePolicy(
        explanation_language="English",
        terminology_language="English",
        teaching_style="Clear, calm step-by-step teaching with short explanations.",
        example_style="Use one simple classroom example that the learner can picture immediately.",
        encouragement_style="Warm encouragement that helps the learner feel capable.",
        forbidden_behaviour=(
            "Do not return an entirely English lesson for Telugu-selected journeys.",
        ),
        concise_prompt_instructions=(
            "English",
            "English academic and technical terminology",
            "Use simple classroom examples and step-by-step guidance.",
        ),
    ),
    "telugu_assisted_english": LanguageProfilePolicy(
        explanation_language="Primarily Telugu",
        terminology_language="Technical, scientific and mathematical terms may remain in English",
        teaching_style="Teach in Telugu with brief English terminology where it improves clarity.",
        example_style="Use one concrete example and explain it in Telugu, with English terms only when needed.",
        encouragement_style="Use supportive Telugu encouragement.",
        forbidden_behaviour=(
            "Do not return an entirely English lesson.",
        ),
        concise_prompt_instructions=(
            "Explanation primarily in Telugu",
            "Technical, scientific and mathematical terms may remain in English",
            "Must not return a fully English lesson",
        ),
    ),
    "pure_telugu": LanguageProfilePolicy(
        explanation_language="Telugu",
        terminology_language="Telugu academic terms wherever available; English terms only in parentheses if useful",
        teaching_style="Teach naturally in Telugu with a calm, age-appropriate learning tone.",
        example_style="Use a simple Telugu example and explain it in Telugu.",
        encouragement_style="Use positive Telugu encouragement with clear progress cues.",
        forbidden_behaviour=(
            "Do not merely translate English word-for-word.",
            "Do not return a fully English lesson.",
            "fully English",
        ),
        concise_prompt_instructions=(
            "తెలుగు",
            "Use correct Telugu academic terms wherever available",
            "English terms may appear in parentheses only when useful",
            "Must not merely translate English word-for-word",
            "Must teach naturally in Telugu",
            "Must not return a fully English lesson",
        ),
    ),
}


def get_language_profile(profile_id: str) -> LanguageProfilePolicy:
    """Return a typed policy for the approved language profile identifiers."""

    if profile_id not in _LANGUAGE_PROFILES:
        raise AIConfigurationError(f"Unsupported language profile: {profile_id}")
    return _LANGUAGE_PROFILES[profile_id]
