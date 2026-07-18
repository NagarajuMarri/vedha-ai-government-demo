"""Deterministic typed-answer evaluation with corrective teaching guidance."""

from __future__ import annotations

import re

from backend.app.practice.models import LearningProfile
from backend.app.practice.repository import PracticeAnswerRepository, practice_answer_repository


class PracticeQuestionNotFoundError(LookupError):
    pass


class PracticeEvaluationService:
    def __init__(self, repository: PracticeAnswerRepository = practice_answer_repository) -> None:
        self._repository = repository

    def evaluate(self, *, practice_set_id: str, question_id: str, student_answer: str) -> dict[str, object]:
        key = self._repository.get(practice_set_id, question_id)
        if key is None:
            raise PracticeQuestionNotFoundError("Practice question was not found or has expired.")
        correct = self._normalize(student_answer) == self._normalize(key.expected_answer)
        feedback, guidance = self._messages(correct, key.learning_profile, key.hint)
        return {"correct": correct, "feedback": feedback, "corrective_guidance": guidance, "attempt_number": 1}

    @staticmethod
    def _normalize(value: str) -> str:
        return re.sub(r"[^\w./-]+", "", value.casefold(), flags=re.UNICODE)

    @staticmethod
    def _messages(correct: bool, profile: LearningProfile, hint: str) -> tuple[str, list[str]]:
        if profile == "pure_telugu":
            if correct:
                return "సరైన సమాధానం! మీరు పద్ధతిని బాగా అర్థం చేసుకున్నారు.", ["మీరు ఉపయోగించిన దశలను మరోసారి పరిశీలించండి."]
            return "ఈ ప్రయత్నంలో చిన్న పొరపాటు ఉంది. తుది సమాధానం చెప్పకుండా మళ్లీ ప్రయత్నిద్దాం.", [hint, "ప్రశ్నలో ఇచ్చిన సంఖ్యలు లేదా ముఖ్య పదాలను గుర్తించండి.", "ఒక్కో దశను విడిగా పూర్తి చేసి సమాధానాన్ని తనిఖీ చేయండి."]
        if profile == "telugu_assisted_english":
            if correct:
                return "Correct answer! మీరు methodను బాగా అర్థం చేసుకున్నారు.", ["మీ stepsను మరోసారి review చేయండి."]
            return "ఈ attemptలో చిన్న mistake ఉంది. Final answer reveal చేయకుండా మళ్లీ guide చేస్తాను.", [hint, "Questionలోని numbers లేదా key wordsను గుర్తించండి.", "ఒక్కో step complete చేసి answerను check చేయండి."]
        if correct:
            return "Correct answer! You have understood the method.", ["Review the steps you used so you can repeat the method."]
        return "There is a small mistake in this attempt. Let us correct the method without revealing only the final answer.", [hint, "Identify the important numbers or key words in the question.", "Complete one step at a time and check your result."]
