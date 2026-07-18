"""Public lesson explain router for Sprint 3B."""

from __future__ import annotations

import inspect
import logging
import time
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, Request, status

from backend.app.ai.lesson_models import LessonGenerationRequest
from backend.app.ai.services.lesson_planner import LessonPlanner
from backend.app.ai.services.lesson_service import LessonGenerationService
from backend.app.core.config import Settings, get_settings
from backend.app.schemas.lessons import ExplainLessonRequest, LessonExplainResponse


router = APIRouter(prefix="/lessons", tags=["lessons"])
logger = logging.getLogger(__name__)


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
    lesson_id = f"lesson-{uuid4()}"
    started_at = time.perf_counter()

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
        concept=payload.concept,
    )

    lesson_result = service.generate_lesson(generation_request)
    if inspect.isawaitable(lesson_result):
        lesson_result = await lesson_result

    latency_ms = round((time.perf_counter() - started_at) * 1000, 2)
    if getattr(service, "last_fallback_reason", None) == "reviewer_rejection":
        logger.warning(
            "Lesson reviewer rejected provider output",
            extra={
                "fallback_reason": "reviewer_rejection",
                "failed_validation_rule": getattr(service, "last_validation_rule", None),
                "provider": "openai",
                "model": getattr(request.app.state.settings, "openai_model", None) or "not_configured",
                "prompt_id": lesson_result.prompt_id,
                "prompt_version": lesson_result.prompt_version,
            },
        )
    logger.info(
        "Lesson generation completed",
        extra={
            "request_id": request_id,
            "lesson_id": lesson_id,
            "provider": lesson_result.source,
            "model": getattr(request.app.state.settings, "openai_model", None) or "not_configured",
            "prompt_id": lesson_result.prompt_id,
            "prompt_version": lesson_result.prompt_version,
            "outcome": "fallback" if lesson_result.fallback_used else "success",
            "fallback_reason": getattr(service, "last_fallback_reason", None),
            "latency_ms": latency_ms,
        },
    )

    return LessonExplainResponse(
        request_id=request_id,
        lesson_id=lesson_id,
        title=lesson_result.title,
        introduction=lesson_result.introduction,
        explanation_steps=lesson_result.explanation_steps,
        example=lesson_result.example,
        key_points=lesson_result.key_points,
        check_question=lesson_result.check_question,
        learning_profile=lesson_result.learning_profile,
        subject=lesson_result.subject,
        class_level=lesson_result.class_level,
        source=lesson_result.source,
        fallback_used=lesson_result.fallback_used,
        created_at=datetime.now(timezone.utc),
    )
