"""Public lesson explain router for Sprint 3B."""

from __future__ import annotations

import inspect
from uuid import uuid4

from fastapi import APIRouter, Depends, Request, status

from backend.app.ai.lesson_models import LessonGenerationRequest
from backend.app.ai.services.lesson_planner import LessonPlanner
from backend.app.ai.services.lesson_reviewer import LessonReviewer
from backend.app.ai.services.lesson_service import LessonGenerationService
from backend.app.core.config import Settings, get_settings
from backend.app.schemas.lessons import ExplainLessonRequest, LessonExplainResponse


router = APIRouter(prefix="/lessons", tags=["lessons"])


def _get_service(settings: Settings = Depends(get_settings)) -> LessonGenerationService:
    """Create the lesson generation service dependency for the route layer."""

    return LessonGenerationService(settings=settings)


@router.post(
    "/explain",
    operation_id="explain_lesson",
    response_model=LessonExplainResponse,
    status_code=status.HTTP_200_OK,
    summary="Explain a lesson concept for the learner",
)
async def explain_lesson(
    request: Request,
    payload: ExplainLessonRequest,
    service: LessonGenerationService = Depends(_get_service),
) -> LessonExplainResponse:
    """Generate a lesson explanation using the approved deterministic route flow."""

    request_id = getattr(request.state, "request_id", str(uuid4()))
    planner = LessonPlanner()
    reviewer = LessonReviewer()

    planner.plan(
        class_level=payload.class_level,
        subject=payload.subject,
        learning_profile=payload.learning_profile,
        question=payload.question,
    )

    generation_request = LessonGenerationRequest(
        class_level=str(payload.class_level),
        subject=payload.subject,
        learning_profile=payload.learning_profile,
        student_question=payload.question,
    )

    lesson_result = service.generate_lesson(generation_request)
    if inspect.isawaitable(lesson_result):
        lesson_result = await lesson_result

    reviewed_lesson = reviewer.review(lesson_result)

    return LessonExplainResponse(
        request_id=request_id,
        lesson_id=f"lesson-{uuid4()}",
        title=reviewed_lesson.title,
        learning_profile=reviewed_lesson.learning_profile,
        subject=reviewed_lesson.subject,
        class_level=reviewed_lesson.class_level,
        source=reviewed_lesson.source,
        fallback_used=reviewed_lesson.fallback_used,
    )
