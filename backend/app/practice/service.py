"""Deterministic, bilingual-safe practice generation for Sprint 4D."""

from __future__ import annotations

from uuid import uuid4

from backend.app.practice.models import LearningProfile, PracticeQuestion, PracticeSet
from backend.app.practice.repository import AnswerKey, PracticeAnswerRepository, practice_answer_repository


class PracticeGenerationService:
    """Generate an exact-composition set and retain answer keys server-side."""

    def __init__(self, repository: PracticeAnswerRepository = practice_answer_repository) -> None:
        self._repository = repository

    def generate(self, *, class_level: int, subject: str, concept: str, learning_profile: LearningProfile) -> PracticeSet:
        practice_set_id = f"practice-{uuid4()}"
        questions: list[PracticeQuestion] = []
        global_position = 0
        for difficulty, total in (("easy", 5), ("medium", 5), ("hard", 5)):
            for position in range(1, total + 1):
                global_position += 1
                prompt, hint, expected_answer = self._content(
                    concept=concept,
                    subject=subject,
                    difficulty=difficulty,
                    position=position,
                    global_position=global_position,
                    profile=learning_profile,
                )
                question_id = f"{difficulty}-{position}-{uuid4().hex[:8]}"
                questions.append(PracticeQuestion(question_id=question_id, difficulty=difficulty, prompt=prompt, hint=hint))
                self._repository.save(
                    practice_set_id,
                    question_id,
                    AnswerKey(
                        expected_answer=expected_answer,
                        hint=hint,
                        learning_profile=learning_profile,
                        concept=concept,
                        source_prompt=prompt,
                    ),
                )
        return PracticeSet(
            practice_set_id=practice_set_id,
            class_level=class_level,
            subject=subject,
            concept=concept,
            learning_profile=learning_profile,
            questions=questions,
        )

    @classmethod
    def _content(
        cls,
        *,
        concept: str,
        subject: str,
        difficulty: str,
        position: int,
        global_position: int,
        profile: LearningProfile,
    ) -> tuple[str, str, str]:
        prompt_en, expected_answer = cls._question_and_answer(concept, global_position)
        if profile == "pure_telugu":
            labels = {"easy": "సులభ", "medium": "మధ్యస్థ", "hard": "కఠిన"}
            prompt_te, expected_answer = cls._question_and_answer_telugu(concept, global_position)
            prompt = f"{labels[difficulty]} ప్రశ్న {position}: {prompt_te} సమాధానాన్ని నమోదు చేయండి."
            hint = cls._telugu_hint(concept)
        elif profile == "telugu_assisted_english":
            labels = {"easy": "సులభ", "medium": "మధ్యస్థ", "hard": "కఠిన"}
            prompt = f"{labels[difficulty]} question {position}: {prompt_en} Answerను enter చేయండి."
            hint = f"{subject}లో {concept} key ruleను గుర్తుచేసుకుని step-by-step solve చేయండి."
        else:
            prompt = f"{difficulty.title()} question {position}: {prompt_en} Enter your final response after working through the steps."
            hint = f"Recall the key {subject} rule for {concept}, then solve it in small steps."
        return prompt, hint, expected_answer

    @staticmethod
    def _telugu_hint(concept: str) -> str:
        hints = {
            "fractions": "లవం, హారం రెండింటినీ ఒకే సామాన్య కారణాంకంతో భాగించండి.",
            "decimals": "దశాంశ బిందువులను ఒకే నిలువు వరుసలో ఉంచి గణించండి.",
            "geometry": "చతురస్రం చుట్టుకొలతకు ఒక భుజం పొడవును నాలుగుతో గుణించండి.",
            "solar system": "గ్రహాల స్థానం మరియు ప్రత్యేక లక్షణాలను గుర్తుచేసుకోండి.",
            "water cycle": "నీరు ఒక స్థితి నుండి మరొక స్థితికి మారే ప్రక్రియను గుర్తించండి.",
            "photosynthesis": "మొక్కలు కాంతి సహాయంతో ఆహారం తయారు చేసే ప్రక్రియను గుర్తుచేసుకోండి.",
            "grammar": "పదం వాక్యంలో చేసే పనిని గుర్తించండి.",
        }
        return hints.get(concept.casefold(), "ప్రశ్నలోని ముఖ్య భావనను గుర్తించి ఒక్కో దశగా పరిష్కరించండి.")

    @staticmethod
    def _question_and_answer_telugu(concept: str, index: int) -> tuple[str, str]:
        normalized = concept.casefold()
        if normalized == "fractions":
            return f"{index}/{index * 2} భిన్నాన్ని సరళీకరించండి.", "1/2"
        if normalized == "decimals":
            return f"{index}.0 + 0.5 విలువను కనుగొనండి.", f"{index}.5"
        if normalized == "geometry":
            return f"ఒక చతురస్రం భుజం పొడవు {index} సెం.మీ. అయితే దాని చుట్టుకొలత ఎన్ని సెం.మీ.?", str(index * 4)
        banks = {
            "solar system": [("ఎర్ర గ్రహం అని ఏ గ్రహాన్ని అంటారు?", "అంగారక గ్రహం"), ("సూర్యునికి అత్యంత సమీపంలోని గ్రహం ఏది?", "బుధ గ్రహం"), ("అతి పెద్ద గ్రహం ఏది?", "గురు గ్రహం")],
            "water cycle": [("ద్రవ నీరు నీటి ఆవిరిగా మారే ప్రక్రియ ఏది?", "ఆవిరీకరణ"), ("నీటి ఆవిరి మేఘాలుగా మారే ప్రక్రియ ఏది?", "సంఘననం"), ("వర్షం భూమికి తిరిగి వచ్చే దశ ఏది?", "అవపాతం")],
            "photosynthesis": [("కిరణజన్య సంయోగక్రియలో మొక్కలు ఏ వాయువును గ్రహిస్తాయి?", "కార్బన్ డయాక్సైడ్"), ("కాంతిని గ్రహించే ఆకుపచ్చ వర్ణద్రవ్యం ఏది?", "పత్రహరితం"), ("ఈ ప్రక్రియలో విడుదలయ్యే వాయువు ఏది?", "ఆక్సిజన్")],
            "grammar": [("‘వేగంగా’ అనే పదం ఏ పదభేదం?", "క్రియావిశేషణం"), ("‘అందమైన’ అనే పదం ఏ పదభేదం?", "విశేషణం"), ("‘ఉపాధ్యాయుడు’ అనే పదం ఏ పదభేదం?", "నామవాచకం")],
        }
        bank = banks.get(normalized)
        if bank:
            question, answer = bank[(index - 1) % len(bank)]
            return f"{question} (అభ్యాస అంశం {index})", answer
        return f"ఈ అభ్యాసంలోని భావన పేరు ఏమిటి: {concept}?", concept

    @staticmethod
    def _question_and_answer(concept: str, index: int) -> tuple[str, str]:
        normalized = concept.casefold()
        if normalized == "fractions":
            return f"Simplify the fraction {index}/{index * 2}.", "1/2"
        if normalized == "decimals":
            return f"Calculate {index}.0 + 0.5.", f"{index}.5"
        if normalized == "geometry":
            return f"A square has side length {index} cm. What is its perimeter in cm?", str(index * 4)
        banks = {
            "solar system": [("Which planet is known as the Red Planet?", "Mars"), ("Which planet is closest to the Sun?", "Mercury"), ("Which planet is the largest?", "Jupiter")],
            "water cycle": [("What process changes liquid water into water vapour?", "Evaporation"), ("What process forms clouds from water vapour?", "Condensation"), ("What stage returns rain to Earth?", "Precipitation")],
            "photosynthesis": [("Which gas do plants take in during photosynthesis?", "Carbon dioxide"), ("What green pigment helps plants absorb light?", "Chlorophyll"), ("Which gas is released during photosynthesis?", "Oxygen")],
            "grammar": [("Identify the part of speech of 'quickly'.", "Adverb"), ("Identify the part of speech of 'beautiful'.", "Adjective"), ("Identify the part of speech of 'teacher'.", "Noun")],
        }
        bank = banks.get(normalized)
        if bank:
            prompt, answer = bank[(index - 1) % len(bank)]
            return f"{prompt} (practice item {index})", answer
        return f"Type the concept name shown in this practice set: {concept}.", concept
