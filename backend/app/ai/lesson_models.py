"""Typed lesson request and response models for the AI infrastructure."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


class LessonGenerationRequest(BaseModel):
    """Typed request for future lesson-generation workflows."""

    model_config = ConfigDict(str_strip_whitespace=True)

    class_level: str = Field(..., min_length=1, max_length=20)
    subject: str = Field(..., min_length=3, max_length=80)
    learning_profile: Literal["english_medium", "telugu_assisted_english", "pure_telugu"]
    student_question: str = Field(..., min_length=8, max_length=1500)


class LessonResult(BaseModel):
    """Structured lesson response returned to application callers."""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(..., min_length=4, max_length=200)
    introduction: str = Field(..., min_length=20, max_length=1000)
    explanation_steps: list[str] = Field(..., min_length=1, max_length=8)
    example: str = Field(..., min_length=10, max_length=1200)
    key_points: list[str] = Field(..., min_length=1, max_length=6)
    check_question: str = Field(..., min_length=8, max_length=500)
    learning_profile: Literal["english_medium", "telugu_assisted_english", "pure_telugu"]
    subject: str = Field(..., min_length=3, max_length=80)
    class_level: str = Field(..., min_length=1, max_length=20)
    source: Literal["openai", "fallback"]
    fallback_used: bool
    prompt_id: str = Field(..., min_length=1, max_length=100)
    prompt_version: str = Field(..., min_length=1, max_length=30)


class GeneratedLessonContent(BaseModel):
    """Strict provider-controlled educational content without application metadata."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    title: str = Field(..., min_length=4, max_length=200)
    introduction: str = Field(..., min_length=20, max_length=1000)
    explanation_steps: list[str] = Field(..., min_length=1, max_length=8)
    example: str = Field(..., min_length=10, max_length=1200)
    key_points: list[str] = Field(..., min_length=1, max_length=6)
    check_question: str = Field(..., min_length=8, max_length=500)
    learning_profile: Literal["english_medium", "telugu_assisted_english", "pure_telugu"]
    subject: str = Field(..., min_length=3, max_length=80)
    class_level: str = Field(..., min_length=1, max_length=20)
