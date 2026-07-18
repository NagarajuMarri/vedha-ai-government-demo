"""Public exact-composition practice API for Sprint 4D."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status

from backend.app.practice.evaluation import PracticeEvaluationService, PracticeQuestionNotFoundError
from backend.app.practice.handwriting import (
    HandwritingEvaluationService,
    HandwritingImageError,
    HandwritingServiceUnavailableError,
)
from backend.app.practice.service import PracticeGenerationService
from backend.app.core.config import Settings, get_settings
from backend.app.schemas.practice import (
    EvaluateHandwritingRequest,
    EvaluatePracticeAnswerRequest,
    GeneratePracticeRequest,
    HandwritingEvaluationResponse,
    PracticeEvaluationResponse,
    PracticeSetResponse,
)

router = APIRouter(prefix="/practice", tags=["practice"])


def _get_service() -> PracticeGenerationService:
    return PracticeGenerationService()


@router.post(
    "/generate",
    operation_id="generate_practice_set",
    response_model=PracticeSetResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate exactly 15 questions for a concept",
)
def generate_practice_set(
    request: Request,
    payload: GeneratePracticeRequest,
    service: PracticeGenerationService = Depends(_get_service),
) -> PracticeSetResponse:
    practice_set = service.generate(
        class_level=payload.class_level,
        subject=payload.subject,
        concept=payload.concept,
        learning_profile=payload.learning_profile,
    )
    return PracticeSetResponse(
        request_id=getattr(request.state, "request_id", str(uuid4())),
        practice_set_id=practice_set.practice_set_id,
        class_level=practice_set.class_level,
        subject=practice_set.subject,
        concept=practice_set.concept,
        learning_profile=practice_set.learning_profile,
        questions=practice_set.questions,
        created_at=datetime.now(timezone.utc),
    )


@router.post(
    "/evaluate",
    operation_id="evaluate_practice_answer",
    response_model=PracticeEvaluationResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate one typed practice answer and return corrective guidance",
)
def evaluate_practice_answer(
    request: Request,
    payload: EvaluatePracticeAnswerRequest,
) -> PracticeEvaluationResponse:
    try:
        result = PracticeEvaluationService().evaluate(
            practice_set_id=payload.practice_set_id,
            question_id=payload.question_id,
            student_answer=payload.student_answer,
            client_attempt_number=payload.attempt_number,
        )
    except PracticeQuestionNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return PracticeEvaluationResponse(
        request_id=getattr(request.state, "request_id", str(uuid4())),
        practice_set_id=payload.practice_set_id,
        question_id=payload.question_id,
        correct=bool(result["correct"]),
        feedback=str(result["feedback"]),
        corrective_guidance=list(result["corrective_guidance"]),
        attempt_number=int(result["attempt_number"]),
        evaluated_at=datetime.now(timezone.utc),
    )


@router.post(
    "/evaluate-handwriting",
    operation_id="evaluate_handwritten_practice",
    response_model=HandwritingEvaluationResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate a JPG or PNG photo of handwritten practice work",
)
def evaluate_handwritten_practice(
    request: Request,
    payload: EvaluateHandwritingRequest,
    settings: Settings = Depends(get_settings),
) -> HandwritingEvaluationResponse:
    try:
        result = HandwritingEvaluationService(settings=settings).evaluate(
            practice_set_id=payload.practice_set_id,
            question_id=payload.question_id,
            image_data_url=payload.image_data_url,
        )
    except PracticeQuestionNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except HandwritingImageError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)) from error
    except HandwritingServiceUnavailableError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Handwritten solution evaluation is temporarily unavailable.",
        ) from error
    return HandwritingEvaluationResponse(
        request_id=getattr(request.state, "request_id", str(uuid4())),
        practice_set_id=payload.practice_set_id,
        question_id=payload.question_id,
        correct=bool(result["correct"]),
        feedback=str(result["feedback"]),
        corrective_guidance=list(result["corrective_guidance"]),
        attempt_number=int(result["attempt_number"]),
        transcribed_work=str(result["transcribed_work"]),
        confidence=float(result["confidence"]),
        evaluated_at=datetime.now(timezone.utc),
    )
