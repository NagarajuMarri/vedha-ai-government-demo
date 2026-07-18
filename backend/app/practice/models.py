"""Validated practice-domain models and exact composition policy."""

from __future__ import annotations

from collections import Counter
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Difficulty = Literal["easy", "medium", "hard"]
LearningProfile = Literal["english_medium", "telugu_assisted_english", "pure_telugu"]


class PracticeQuestion(BaseModel):
    """One safely structured practice question."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    question_id: str = Field(..., min_length=1, max_length=100)
    difficulty: Difficulty
    prompt: str = Field(..., min_length=8, max_length=600)
    hint: str = Field(..., min_length=4, max_length=400)


class PracticeSet(BaseModel):
    """A concept practice set that must contain exactly 5/5/5 questions."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    practice_set_id: str = Field(..., min_length=1, max_length=100)
    class_level: int = Field(..., ge=1, le=12)
    subject: str = Field(..., min_length=3, max_length=80)
    concept: str = Field(..., min_length=2, max_length=120)
    learning_profile: LearningProfile
    questions: list[PracticeQuestion] = Field(..., min_length=15, max_length=15)

    @model_validator(mode="after")
    def enforce_exact_composition(self) -> "PracticeSet":
        counts = Counter(question.difficulty for question in self.questions)
        expected = {"easy": 5, "medium": 5, "hard": 5}
        if dict(counts) != expected:
            raise ValueError("Practice set must contain exactly 5 easy, 5 medium, and 5 hard questions.")
        ids = [question.question_id for question in self.questions]
        prompts = [question.prompt.casefold() for question in self.questions]
        if len(ids) != len(set(ids)) or len(prompts) != len(set(prompts)):
            raise ValueError("Practice questions must have unique IDs and prompts.")
        return self
