"""Deterministic, bilingual-safe practice generation for Sprint 4D."""

from __future__ import annotations

from uuid import uuid4

from backend.app.practice.models import LearningProfile, PracticeQuestion, PracticeSet


class PracticeGenerationService:
    """Generate a safe exact-composition set without requiring a live provider."""

    def generate(
        self,
        *,
        class_level: int,
        subject: str,
        concept: str,
        learning_profile: LearningProfile,
    ) -> PracticeSet:
        questions: list[PracticeQuestion] = []
        for difficulty, total in (("easy", 5), ("medium", 5), ("hard", 5)):
            for position in range(1, total + 1):
                prompt, hint = self._content(
                    concept=concept,
                    subject=subject,
                    difficulty=difficulty,
                    position=position,
                    profile=learning_profile,
                )
                questions.append(
                    PracticeQuestion(
                        question_id=f"{difficulty}-{position}-{uuid4().hex[:8]}",
                        difficulty=difficulty,
                        prompt=prompt,
                        hint=hint,
                    )
                )
        return PracticeSet(
            practice_set_id=f"practice-{uuid4()}",
            class_level=class_level,
            subject=subject,
            concept=concept,
            learning_profile=learning_profile,
            questions=questions,
        )

    @staticmethod
    def _content(*, concept: str, subject: str, difficulty: str, position: int, profile: LearningProfile) -> tuple[str, str]:
        if profile == "pure_telugu":
            labels = {"easy": "సులభ", "medium": "మధ్యస్థ", "hard": "కఠిన"}
            prompt = f"{concept} అంశంపై {labels[difficulty]} స్థాయి అభ్యాస ప్రశ్న {position}: మీ ఆలోచనను దశలవారీగా వివరించండి."
            hint = f"{subject}లో {concept} యొక్క ప్రధాన నియమాన్ని గుర్తుచేసుకుని చిన్న దశలుగా పరిష్కరించండి."
        elif profile == "telugu_assisted_english":
            labels = {"easy": "సులభ", "medium": "మధ్యస్థ", "hard": "కఠిన"}
            prompt = f"{concept}పై {labels[difficulty]} స్థాయి practice question {position}: answerను stepsతో explain చేయండి."
            hint = f"{subject}లో {concept} key ruleను గుర్తుచేసుకుని ఒక్కో stepగా ప్రయత్నించండి."
        else:
            prompt = f"{concept} {difficulty} practice question {position}: explain your reasoning step by step."
            hint = f"Recall the key {subject} rule for {concept}, then solve it in small steps."
        return prompt, hint
