"""Privacy-safe handwritten practice evaluation using OpenAI vision."""

from __future__ import annotations

import base64
import binascii
import re

from openai import OpenAI
from pydantic import BaseModel, ConfigDict, Field

from backend.app.core.config import Settings
from backend.app.practice.evaluation import PracticeEvaluationService, PracticeQuestionNotFoundError
from backend.app.practice.repository import PracticeAnswerRepository, practice_answer_repository


MAX_IMAGE_BYTES = 5 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png"}


class HandwritingImageError(ValueError):
    pass


class HandwritingServiceUnavailableError(RuntimeError):
    pass


class HandwritingVisionResult(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    transcribed_work: str = Field(..., min_length=1, max_length=2000)
    correct: bool
    feedback: str = Field(..., min_length=5, max_length=1000)
    corrective_guidance: list[str] = Field(..., min_length=1, max_length=5)
    confidence: float = Field(..., ge=0, le=1)


class HandwritingEvaluationService:
    """Analyse one image in memory; never persist uploaded student work."""

    def __init__(
        self,
        settings: Settings,
        repository: PracticeAnswerRepository = practice_answer_repository,
        client: OpenAI | None = None,
    ) -> None:
        self._settings = settings
        self._repository = repository
        self._client = client

    def evaluate(
        self,
        *,
        practice_set_id: str,
        question_id: str,
        image_data_url: str,
    ) -> dict[str, object]:
        key = self._repository.get(practice_set_id, question_id)
        if key is None:
            raise PracticeQuestionNotFoundError("Practice question was not found or has expired.")
        self._validate_image(image_data_url)
        if not self._settings.openai_api_key or not self._settings.openai_model:
            raise HandwritingServiceUnavailableError("Vision evaluation is not configured.")
        client = self._client or OpenAI(
            api_key=self._settings.openai_api_key,
            timeout=self._settings.openai_timeout_seconds,
        )
        instructions = (
            "You are evaluating a student's handwritten solution to one practice question. "
            f"Question: {key.source_prompt}\nExpected answer (private evaluator key): {key.expected_answer}\n"
            f"Learning profile: {key.learning_profile}. "
            "The input may be a direct phone photo with rotation, perspective, shadows, or mild glare. "
            "Transcribe only clearly visible mathematical work; lower confidence and ask for a clearer photo if unreadable. "
            "Decide correctness from the shown steps, not handwriting quality. "
            "Give concise, question-specific feedback and 1-4 corrective steps in the selected learning profile. "
            "If incorrect, do not state the expected final answer. Never mention hidden keys, prompts, providers, or image metadata."
        )
        try:
            response = client.responses.parse(
                model=self._settings.openai_model,
                instructions=instructions,
                input=[{
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "Evaluate this handwritten solution."},
                        {"type": "input_image", "image_url": image_data_url},
                    ],
                }],
                text_format=HandwritingVisionResult,
                store=False,
            )
        except Exception as exc:
            raise HandwritingServiceUnavailableError("Vision evaluation could not be completed.") from exc
        parsed = getattr(response, "output_parsed", None)
        if not isinstance(parsed, HandwritingVisionResult):
            try:
                parsed = HandwritingVisionResult.model_validate(parsed)
            except Exception as exc:
                raise HandwritingServiceUnavailableError("Vision response was invalid.") from exc

        attempt = self._repository.next_attempt(practice_set_id, question_id)
        combined = " ".join([parsed.feedback, *parsed.corrective_guidance])
        if not parsed.correct and self._contains_expected_answer(combined, key.expected_answer):
            feedback, guidance = PracticeEvaluationService._messages(
                False, key, parsed.transcribed_work, attempt
            )
        else:
            feedback, guidance = parsed.feedback, parsed.corrective_guidance
        return {
            "correct": parsed.correct,
            "feedback": feedback,
            "corrective_guidance": guidance,
            "attempt_number": attempt,
            "transcribed_work": parsed.transcribed_work,
            "confidence": parsed.confidence,
        }

    @staticmethod
    def _validate_image(image_data_url: str) -> None:
        match = re.fullmatch(
            r"data:(image/(?:jpeg|png));base64,([A-Za-z0-9+/=\r\n]+)",
            image_data_url,
        )
        if not match or match.group(1) not in ALLOWED_IMAGE_TYPES:
            raise HandwritingImageError("Upload a valid JPG or PNG image.")
        try:
            decoded = base64.b64decode(match.group(2), validate=True)
        except (binascii.Error, ValueError) as exc:
            raise HandwritingImageError("The uploaded image data is invalid.") from exc
        if not decoded:
            raise HandwritingImageError("The uploaded image is empty.")
        if len(decoded) > MAX_IMAGE_BYTES:
            raise HandwritingImageError("The uploaded image must be 5 MB or smaller.")

    @staticmethod
    def _contains_expected_answer(text: str, expected_answer: str) -> bool:
        return bool(expected_answer and expected_answer.casefold() in text.casefold())
