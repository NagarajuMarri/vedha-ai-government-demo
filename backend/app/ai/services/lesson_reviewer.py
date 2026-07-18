"""Deterministic safety and contract review for generated lessons."""

from __future__ import annotations

import re
import unicodedata

from backend.app.ai.exceptions import AIReviewerRejectionError
from backend.app.ai.lesson_models import LessonGenerationRequest, LessonResult


_TELUGU_PATTERN = re.compile(r"[\u0C00-\u0C7F]")
_LEAK_MARKERS = ("system prompt", "developer message", "hidden instruction", "chain of thought", "openai")
_MOJIBAKE_MARKERS = ("à°", "à±", "Ã", "Â", "è", "ç", "¤", "¡", "[OBJ]", "\ufffc")
_ADVANCED_FRACTION_TERMS = (
    "lcm", "hcf", "gcf", "lowest common multiple", "highest common factor",
    "improper fraction", "mixed number", "fraction addition", "fraction subtraction",
    "కనిష్ఠ సామాన్య గుణిజం", "గరిష్ఠ సామాన్య కారణాంకం", "అపక్రమ భిన్నం",
    "మిశ్ర సంఖ్య", "భిన్నాల కూడిక", "భిన్నాల తీసివేత",
)
_INCORRECT_TERMS = ("అపరిమిత భిన్నం",)


class LessonReviewer:
    """Reject invalid or policy-breaking provider output without another model call."""

    def review(self, lesson: LessonResult, request: LessonGenerationRequest | None = None) -> LessonResult:
        """Normalize safe strings and enforce request and language invariants."""

        if request and (
            lesson.class_level != request.class_level
            or lesson.subject != request.subject
            or lesson.learning_profile != request.learning_profile
        ):
            raise AIReviewerRejectionError("canonical_metadata_mismatch")

        text_fields = [lesson.title, lesson.introduction, lesson.example, lesson.check_question]
        list_fields = [lesson.explanation_steps, lesson.key_points]
        if any(not value or not value.strip() for value in text_fields):
            raise AIReviewerRejectionError("required_text_empty")
        if any(not values or any(not value or not value.strip() for value in values) for values in list_fields):
            raise AIReviewerRejectionError("list_content_empty")

        all_content = " ".join(text_fields + [item for values in list_fields for item in values])
        if any(marker in all_content.lower() for marker in _LEAK_MARKERS):
            raise AIReviewerRejectionError("internal_reference_detected")
        if any(marker.casefold() in all_content.casefold() for marker in _MOJIBAKE_MARKERS):
            raise AIReviewerRejectionError("encoding_artifact")
        if lesson.learning_profile == "pure_telugu":
            for value in text_fields + [item for values in list_fields for item in values]:
                if not _TELUGU_PATTERN.search(value):
                    raise AIReviewerRejectionError("pure_telugu_script_missing")
                if self._contains_unexpected_script(value):
                    raise AIReviewerRejectionError("unexpected_script")

        if lesson.source == "openai" and request:
            self._review_educational_quality(lesson, request, all_content)

        return lesson.model_copy(update={
            "title": lesson.title.strip(),
            "introduction": lesson.introduction.strip(),
            "explanation_steps": [step.strip() for step in lesson.explanation_steps],
            "example": lesson.example.strip(),
            "key_points": [point.strip() for point in lesson.key_points],
            "check_question": lesson.check_question.strip(),
        })

    @staticmethod
    def _contains_unexpected_script(value: str) -> bool:
        """Reject unrelated scripts and recognizable encoding corruption."""

        if any(marker in value for marker in _MOJIBAKE_MARKERS):
            return True
        for character in value:
            if not character.isalpha():
                continue
            codepoint = ord(character)
            if 0x0C00 <= codepoint <= 0x0C7F:
                continue
            if "LATIN" in unicodedata.name(character, ""):
                continue
            return True
        return False

    def _review_educational_quality(
        self,
        lesson: LessonResult,
        request: LessonGenerationRequest,
        all_content: str,
    ) -> None:
        """Apply deterministic scope and elementary Mathematics invariants."""

        content = all_content.casefold()
        question = request.student_question.casefold()
        if any(term in content for term in _INCORRECT_TERMS):
            raise AIReviewerRejectionError("terminology_error")

        if request.subject != "Mathematics" or not request.class_level.isdigit():
            return
        if int(request.class_level) <= 5 and len(lesson.explanation_steps) > 4:
            raise AIReviewerRejectionError("excessive_scope")
        if "fraction" not in question and "భిన్న" not in question:
            return

        requested_advanced = {term for term in _ADVANCED_FRACTION_TERMS if term in question}
        introduced_advanced = {term for term in _ADVANCED_FRACTION_TERMS if term in content}
        if introduced_advanced - requested_advanced:
            raise AIReviewerRejectionError("excessive_scope")

        asks_for_parts = any(term in question for term in ("numerator", "denominator", "లవం", "హారం"))
        if asks_for_parts and lesson.learning_profile == "pure_telugu":
            has_numerator_position = bool(re.search(r"లవం[^.!?\n]{0,60}(పై|పైన|ఎగువ)", all_content))
            has_denominator_position = bool(re.search(r"హారం[^.!?\n]{0,60}(కింద|దిగువ)", all_content))
            reversed_position = bool(
                re.search(r"లవం[^.!?\n]{0,60}(కింద|దిగువ)", all_content)
                or re.search(r"హారం[^.!?\n]{0,60}(పై|పైన|ఎగువ)", all_content)
            )
            if reversed_position or not (has_numerator_position and has_denominator_position):
                raise AIReviewerRejectionError("malformed_fraction_explanation")
        elif asks_for_parts and lesson.learning_profile == "english_medium":
            has_numerator_position = bool(re.search(r"numerator[^.!?\n]{0,60}(top|above)", content))
            has_denominator_position = bool(re.search(r"denominator[^.!?\n]{0,60}(bottom|below)", content))
            if not (has_numerator_position and has_denominator_position):
                raise AIReviewerRejectionError("malformed_fraction_explanation")
