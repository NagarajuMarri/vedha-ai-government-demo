"""In-memory answer-key repository for the controlled Sprint 4D demo."""

from __future__ import annotations

from dataclasses import dataclass

from backend.app.practice.models import LearningProfile


@dataclass(frozen=True)
class AnswerKey:
    expected_answer: str
    hint: str
    learning_profile: LearningProfile


class PracticeAnswerRepository:
    """Keep answer keys server-side for one demo process; SQLite persistence follows."""

    def __init__(self) -> None:
        self._keys: dict[tuple[str, str], AnswerKey] = {}

    def save(self, practice_set_id: str, question_id: str, key: AnswerKey) -> None:
        self._keys[(practice_set_id, question_id)] = key

    def get(self, practice_set_id: str, question_id: str) -> AnswerKey | None:
        return self._keys.get((practice_set_id, question_id))


practice_answer_repository = PracticeAnswerRepository()
