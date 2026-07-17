"""Public lesson API request and response schemas for Sprint 3B."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


class ExplainLessonRequest(BaseModel):
    """Typed request body accepted by the public lesson explain endpoint."""

    model_config = ConfigDict(str_strip_whitespace=True)

    student_name: str = Field(..., min_length=2, max_length=80)
    class_level: int = Field(..., ge=1, le=12)
    subject: str = Field(..., min_length=3, max_length=80)
    learning_profile: Literal["english_medium", "telugu_assisted_english", "pure_telugu"]
    question: str = Field(..., min_length=8, max_length=4000)


class LessonExplainResponse(BaseModel):
    """Public lesson response shape for the explain endpoint."""

    model_config = ConfigDict(str_strip_whitespace=True)

    request_id: str = Field(..., min_length=1, max_length=200)
    lesson_id: str = Field(..., min_length=1, max_length=200)
    title: str = Field(..., min_length=4, max_length=200)
    learning_profile: Literal["english_medium", "telugu_assisted_english", "pure_telugu"]
    subject: str = Field(..., min_length=3, max_length=80)
    class_level: str = Field(..., min_length=1, max_length=20)
    source: Literal["openai", "fallback"]
    fallback_used: bool
