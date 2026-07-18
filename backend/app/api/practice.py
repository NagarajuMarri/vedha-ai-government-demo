"""Public exact-composition practice API for Sprint 4D."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, Request, status

from backend.app.practice.service import PracticeGenerationService
from backend.app.schemas.practice import GeneratePracticeRequest, PracticeSetResponse

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
