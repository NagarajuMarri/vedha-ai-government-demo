"""Deterministic typed-answer evaluation with question-specific corrective guidance."""

from __future__ import annotations

from math import gcd
import re

from backend.app.practice.models import LearningProfile
from backend.app.practice.repository import AnswerKey, PracticeAnswerRepository, practice_answer_repository


class PracticeQuestionNotFoundError(LookupError):
    pass


class PracticeEvaluationService:
    def __init__(self, repository: PracticeAnswerRepository = practice_answer_repository) -> None:
        self._repository = repository

    def evaluate(self, *, practice_set_id: str, question_id: str, student_answer: str) -> dict[str, object]:
        key = self._repository.get(practice_set_id, question_id)
        if key is None:
            raise PracticeQuestionNotFoundError("Practice question was not found or has expired.")
        attempt_number = self._repository.next_attempt(practice_set_id, question_id)
        correct = self._normalize(student_answer) == self._normalize(key.expected_answer)
        feedback, guidance = self._messages(correct, key, student_answer, attempt_number)
        return {
            "correct": correct,
            "feedback": feedback,
            "corrective_guidance": guidance,
            "attempt_number": attempt_number,
        }

    @staticmethod
    def _normalize(value: str) -> str:
        return re.sub(r"[^\w./-]+", "", value.casefold(), flags=re.UNICODE)

    @classmethod
    def _messages(
        cls,
        correct: bool,
        key: AnswerKey,
        student_answer: str,
        attempt_number: int,
    ) -> tuple[str, list[str]]:
        profile = key.learning_profile
        if correct:
            if profile == "pure_telugu":
                return f"సరైన సమాధానం! {attempt_number}వ ప్రయత్నంలో పద్ధతిని సరిగ్గా ఉపయోగించారు.", [
                    "ప్రశ్నలోని సంఖ్యలపై ఇదే పద్ధతిని ఎలా ఉపయోగించారో ఒకసారి గుర్తుచేసుకోండి."
                ]
            if profile == "telugu_assisted_english":
                return f"Correct answer! {attempt_number}వ attemptలో methodను సరిగ్గా use చేశారు.", [
                    "ఇదే methodను next questionలో repeat చేయండి."
                ]
            return f"Correct answer on attempt {attempt_number}! You used the method successfully.", [
                "Briefly review the calculation so you can repeat the method."
            ]

        if attempt_number >= 2:
            return cls._worked_solution(key, student_answer, attempt_number)

        normalized_concept = key.concept.casefold()
        if normalized_concept == "fractions":
            return cls._fraction_guidance(key, student_answer, attempt_number)
        return cls._concept_guidance(key, student_answer, attempt_number)

    @staticmethod
    def _worked_solution(
        key: AnswerKey,
        student_answer: str,
        attempt_number: int,
    ) -> tuple[str, list[str]]:
        source_match = re.search(r"(\d+)\s*/\s*(\d+)", key.source_prompt)
        if key.concept.casefold() == "fractions" and source_match:
            numerator, denominator = int(source_match.group(1)), int(source_match.group(2))
            divisor = gcd(numerator, denominator)
            solved_numerator = numerator // divisor
            solved_denominator = denominator // divisor
            final_answer = f"{solved_numerator}/{solved_denominator}"
            if key.learning_profile == "pure_telugu":
                return f"{attempt_number}వ ప్రయత్నం తర్వాత పూర్తి పరిష్కారాన్ని చూద్దాం. సరైన సమాధానం {final_answer}.", [
                    f"ఇచ్చిన భిన్నం {numerator}/{denominator}.",
                    f"{numerator}, {denominator}ల గరిష్ఠ సామాన్య కారణాంకం {divisor}.",
                    f"లవం: {numerator} ÷ {divisor} = {solved_numerator}; హారం: {denominator} ÷ {divisor} = {solved_denominator}.",
                    f"కాబట్టి సరళీకరించిన భిన్నం {final_answer}.",
                ]
            if key.learning_profile == "telugu_assisted_english":
                return f"Attempt {attempt_number} తర్వాత complete solution చూద్దాం. Correct answer {final_answer}.", [
                    f"Given fraction: {numerator}/{denominator}.",
                    f"{numerator}, {denominator}కి GCF = {divisor}.",
                    f"Numerator: {numerator} ÷ {divisor} = {solved_numerator}; denominator: {denominator} ÷ {divisor} = {solved_denominator}.",
                    f"Therefore simplified fraction = {final_answer}.",
                ]
            return f"After attempt {attempt_number}, here is the complete solution. The correct answer is {final_answer}.", [
                f"Start with the given fraction {numerator}/{denominator}.",
                f"The greatest common divisor of {numerator} and {denominator} is {divisor}.",
                f"Divide both by {divisor}: {numerator} ÷ {divisor} = {solved_numerator} and {denominator} ÷ {divisor} = {solved_denominator}.",
                f"Therefore, the simplified fraction is {final_answer}.",
            ]

        if key.learning_profile == "pure_telugu":
            return f"{attempt_number}వ ప్రయత్నం తర్వాత పూర్తి సమాధానం: {key.expected_answer}.", [
                f"ప్రశ్న: {key.source_prompt}",
                f"సూచనను వర్తింపజేయండి: {key.hint}",
                f"సరైన సమాధానం: {key.expected_answer}.",
            ]
        if key.learning_profile == "telugu_assisted_english":
            return f"Attempt {attempt_number} తర్వాత complete answer: {key.expected_answer}.", [
                f"Question: {key.source_prompt}",
                f"Apply the hint: {key.hint}",
                f"Correct answer: {key.expected_answer}.",
            ]
        return f"After attempt {attempt_number}, the correct answer is {key.expected_answer}.", [
            f"Question: {key.source_prompt}",
            f"Apply the concept-specific hint: {key.hint}",
            f"Correct answer: {key.expected_answer}.",
        ]

    @staticmethod
    def _fraction_guidance(
        key: AnswerKey,
        student_answer: str,
        attempt_number: int,
    ) -> tuple[str, list[str]]:
        source_match = re.search(r"(\d+)\s*/\s*(\d+)", key.source_prompt)
        answer_match = re.fullmatch(r"\s*(\d+)\s*/\s*(\d+)\s*", student_answer)
        profile = key.learning_profile
        if not source_match:
            return PracticeEvaluationService._concept_guidance(key, student_answer, attempt_number)
        numerator, denominator = (int(source_match.group(1)), int(source_match.group(2)))
        divisor = gcd(numerator, denominator)

        if not answer_match:
            if profile == "pure_telugu":
                return f"{attempt_number}వ ప్రయత్నాన్ని ఇంకా తనిఖీ చేయాలి.", [
                    "సమాధానాన్ని లవం/హారం రూపంలో రాయండి, ఉదాహరణకు 3/4.",
                    f"ఇచ్చిన లవం {numerator}, హారం {denominator}కు గరిష్ఠ సామాన్య కారణాంకాన్ని కనుగొనండి.",
                    "లవం, హారం రెండింటినీ అదే కారణాంకంతో భాగించి మళ్లీ నమోదు చేయండి.",
                ]
            if profile == "telugu_assisted_english":
                return f"Attempt {attempt_number}ను ఇంకా check చేయాలి.", [
                    "Answerను numerator/denominator formatలో enter చేయండి, example 3/4.",
                    f"Given numerator {numerator}, denominator {denominator}కి GCF find చేయండి.",
                    "రెండింటినీ same GCFతో divide చేసి retry చేయండి.",
                ]
            return f"Attempt {attempt_number} needs a fraction in a checkable format.", [
                "Enter the answer as numerator/denominator, for example 3/4.",
                f"Find the greatest common divisor of {numerator} and {denominator}.",
                "Divide both numbers by that same divisor, then retry.",
            ]

        attempted_numerator, attempted_denominator = (
            int(answer_match.group(1)),
            int(answer_match.group(2)),
        )
        left_product = attempted_numerator * denominator
        right_product = attempted_denominator * numerator

        if profile == "pure_telugu":
            return f"{attempt_number}వ ప్రయత్నం సరిపోలలేదు. మీ {student_answer.strip()} సమాధానాన్ని దశలవారీగా తనిఖీ చేద్దాం.", [
                f"మొదటి భిన్నంలోని లవం {numerator}, హారం {denominator}. వాటి గరిష్ఠ సామాన్య కారణాంకం {divisor}.",
                f"సమానత్వ తనిఖీ: {attempted_numerator} × {denominator} = {left_product}; {attempted_denominator} × {numerator} = {right_product}. ఈ ఫలితాలు సమానంగా ఉండాలి.",
                "మూల లవం, హారం రెండింటినీ ఒకే గరిష్ఠ సామాన్య కారణాంకంతో భాగించి కొత్త భిన్నాన్ని నమోదు చేయండి.",
            ]
        if profile == "telugu_assisted_english":
            return f"Attempt {attempt_number}లో {student_answer.strip()} match కాలేదు. Calculationను step-by-step check చేద్దాం.", [
                f"Original numerator {numerator}, denominator {denominator}; వాటి GCF {divisor}.",
                f"Equivalence check: {attempted_numerator} × {denominator} = {left_product}; {attempted_denominator} × {numerator} = {right_product}. రెండు results equal కావాలి.",
                "Original numerator, denominator రెండింటినీ same GCFతో divide చేసి retry చేయండి.",
            ]
        return f"Attempt {attempt_number} ({student_answer.strip()}) is not equivalent to the question fraction.", [
            f"The original numerator is {numerator}, the denominator is {denominator}, and their greatest common divisor is {divisor}.",
            f"Cross-check equivalence: {attempted_numerator} × {denominator} = {left_product}, while {attempted_denominator} × {numerator} = {right_product}. These must match.",
            "Divide the original numerator and denominator by the same greatest common divisor, then enter the simplified fraction.",
        ]

    @staticmethod
    def _concept_guidance(
        key: AnswerKey,
        student_answer: str,
        attempt_number: int,
    ) -> tuple[str, list[str]]:
        concept = key.concept
        if key.learning_profile == "pure_telugu":
            return f"{attempt_number}వ ప్రయత్నంలోని “{student_answer.strip()}” సమాధానం సరిపోలలేదు.", [
                f"ప్రశ్నను మళ్లీ చదవండి: {key.source_prompt}",
                f"{concept}కు సంబంధించిన ఈ సూచనను ఉపయోగించండి: {key.hint}",
                "ప్రశ్నలో అడిగిన ప్రక్రియ, లక్షణం లేదా గణనను గుర్తించి మళ్లీ సమాధానం ఇవ్వండి.",
            ]
        if key.learning_profile == "telugu_assisted_english":
            return f"Attempt {attempt_number}లో “{student_answer.strip()}” answer match కాలేదు.", [
                f"Questionను మళ్లీ read చేయండి: {key.source_prompt}",
                f"{concept} hintను apply చేయండి: {key.hint}",
                "Asked process, property లేదా calculationను identify చేసి retry చేయండి.",
            ]
        return f"Attempt {attempt_number} ({student_answer.strip()}) does not match this {concept} question.", [
            f"Read the exact question again: {key.source_prompt}",
            f"Apply this concept-specific hint: {key.hint}",
            "Identify whether the question asks for a process, property, term, or calculation, then retry.",
        ]
