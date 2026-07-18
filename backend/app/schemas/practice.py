"""Public practice API schemas for Sprint 4D."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from backend.app.practice.models import LearningProfile, PracticeQuestion


class GeneratePracticeRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    student_name: str = Field(..., min_length=2, max_length=80)
    class_level: int = Field(..., ge=1, le=12)
    subject: str = Field(..., min_length=3, max_length=80)
    concept: str = Field(..., min_length=2, max_length=120)
    learning_profile: LearningProfile


class PracticeSetResponse(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    request_id: str
    practice_set_id: str
    class_level: int
    subject: str
    concept: str
    learning_profile: LearningProfile
    questions: list[PracticeQuestion] = Field(..., min_length=15, max_length=15)
    created_at: datetime


class EvaluatePracticeAnswerRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    practice_set_id: str = Field(..., min_length=1, max_length=100)
    question_id: str = Field(..., min_length=1, max_length=100)
    student_answer: str = Field(..., min_length=1, max_length=1000)


class PracticeEvaluationResponse(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    request_id: str
    practice_set_id: str
    question_id: str
    correct: bool
    feedback: str = Field(..., min_length=5, max_length=1000)
    corrective_guidance: list[str] = Field(..., min_length=1, max_length=5)
    attempt_number: int = Field(..., ge=1)
    evaluated_at: datetime
