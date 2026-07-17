"""Versioned prompt definitions for governed lesson generation."""

from __future__ import annotations

from dataclasses import dataclass

from backend.app.ai.exceptions import AIConfigurationError


SUPPORTED_PROFILES = (
    "english_medium",
    "telugu_assisted_english",
    "pure_telugu",
)


@dataclass(frozen=True, slots=True)
class PromptDefinition:
    """Metadata and subject rules for one immutable prompt version."""

    prompt_id: str
    prompt_version: str
    subject: str
    supported_learning_profiles: tuple[str, ...]
    teaching_rules: tuple[str, ...]
    builder_reference: str = "LessonPromptBuilder"
    active: bool = True


_GENERAL_RULES = (
    "Directly answer the student's actual question.",
    "Teach the concept before checking understanding.",
    "Use age-appropriate, step-by-step explanations for independent home learning.",
    "Include one clear, simple example, meaningful key points, and one check question.",
    "Do not mention AI models, providers, system prompts, or hidden instructions.",
    "Keep the lesson focused and reasonably concise.",
)


PROMPT_REGISTRY: tuple[PromptDefinition, ...] = (
    PromptDefinition("vedha_general_teacher_v1", "1.0.0", "General", SUPPORTED_PROFILES, _GENERAL_RULES),
    PromptDefinition("vedha_mathematics_teacher_v1", "1.1.0", "Mathematics", SUPPORTED_PROFILES, _GENERAL_RULES + (
        "For elementary classes, begin with one concrete example and then explain the concept.",
        "Use one mathematical idea per sentence and preserve accurate notation.",
        "For a fraction a/b, verify that a is the numerator above the fraction bar and b is the denominator below it.",
        "Read 6/8 naturally as six of eight equal parts; in Telugu use ఎనిమిదిలో ఆరు భాగాలు or an equivalent natural phrase.",
        "Never invent number words or confuse numerator and denominator positions.",
        "Avoid advanced classification, operations, simplification, LCM, or HCF unless the question requires them.",
        "Use established Telugu mathematics terms when the profile requires them.",
    )),
    PromptDefinition("vedha_science_teacher_v1", "1.0.0", "Science", SUPPORTED_PROFILES, _GENERAL_RULES + (
        "Explain observable phenomena and connect them to daily life.",
        "Distinguish scientific facts from simplified analogies.",
        "Do not provide unsafe experimental instructions.",
    )),
    PromptDefinition("vedha_english_teacher_v1", "1.0.0", "English", SUPPORTED_PROFILES, _GENERAL_RULES + (
        "Teach grammar, vocabulary, comprehension, or writing according to the question.",
        "Give clear examples and avoid advanced grammar labels for younger classes.",
    )),
    PromptDefinition("vedha_telugu_teacher_v1", "1.0.0", "Telugu", SUPPORTED_PROFILES, _GENERAL_RULES + (
        "Use correct Telugu grammar and vocabulary.",
        "Keep literary complexity appropriate to the learner's class.",
        "Support reading, writing, grammar, and comprehension questions.",
    )),
    PromptDefinition("vedha_social_studies_teacher_v1", "1.0.0", "Social Studies", SUPPORTED_PROFILES, _GENERAL_RULES + (
        "Explain history, geography, civics, and economics accurately and neutrally.",
        "Distinguish historical fact from interpretation.",
        "Avoid unsupported political claims.",
    )),
)


def get_active_prompt(subject: str, learning_profile: str) -> PromptDefinition:
    """Return the active versioned prompt for a subject and profile."""

    for definition in PROMPT_REGISTRY:
        if definition.subject == subject and definition.active:
            if learning_profile not in definition.supported_learning_profiles:
                raise AIConfigurationError("Learning profile is not supported by the active prompt")
            return definition
    raise AIConfigurationError(f"No active prompt is configured for subject: {subject}")
