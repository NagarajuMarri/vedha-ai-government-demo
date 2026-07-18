"""In-memory answer-key repository for the controlled Sprint 4D demo."""

from __future__ import annotations

from dataclasses import dataclass

from backend.app.practice.models import LearningProfile


@dataclass(frozen=True)
class AnswerKey:
    expected_answer: str
    hint: str
    learning_profile: LearningProfile
    concept: str
    source_prompt: str


class PracticeAnswerRepository:
    """Keep answer keys and attempt counts server-side for one demo process."""

    def __init__(self) -> None:
        self._keys: dict[tuple[str, str], AnswerKey] = {}
        self._attempts: dict[tuple[str, str], int] = {}

    def save(self, practice_set_id: str, question_id: str, key: AnswerKey) -> None:
        identity = (practice_set_id, question_id)
        self._keys[identity] = key
        self._attempts[identity] = 0

    def get(self, practice_set_id: str, question_id: str) -> AnswerKey | None:
        return self._keys.get((practice_set_id, question_id))

    def next_attempt(self, practice_set_id: str, question_id: str) -> int:
        identity = (practice_set_id, question_id)
        self._attempts[identity] = self._attempts.get(identity, 0) + 1
        return self._attempts[identity]


practice_answer_repository = PracticeAnswerRepository()
