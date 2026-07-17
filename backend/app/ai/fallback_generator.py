"""Deterministic fallback lesson generator for approved recoverable failures."""

from __future__ import annotations

from backend.app.ai.lesson_models import LessonGenerationRequest, LessonResult


class DeterministicFallbackLessonGenerator:
    """Provide safe, provider-independent fallback lesson content."""

    def generate(self, request: LessonGenerationRequest) -> LessonResult:
        """Create deterministic fallback output from the normalized request."""

        profile = request.learning_profile
        content = self._build_content(profile, request)

        return LessonResult(
            title=content["title"],
            introduction=content["introduction"],
            explanation_steps=content["explanation_steps"],
            example=content["example"],
            key_points=content["key_points"],
            check_question=content["check_question"],
            learning_profile=profile,
            subject=request.subject,
            class_level=request.class_level,
            source="fallback",
            fallback_used=True,
        )

    def _build_content(self, profile: str, request: LessonGenerationRequest) -> dict[str, str | list[str]]:
        subject = request.subject
        if profile == "english_medium":
            return {
                "title": f"Understanding the foundation of {subject}",
                "introduction": f"This lesson builds the main idea in {subject} step by step and connects it to your question in an age-appropriate way.",
                "explanation_steps": [
                    f"First, identify the central idea in {subject} and describe what it means in simple words.",
                    "Next, connect that idea to something familiar from daily life or the classroom.",
                    "Finally, use the example and check question to explain the idea in your own words.",
                ],
                "example": f"Think of one simple situation involving {subject}. Use it to explore this question: {request.student_question}",
                "key_points": [
                    "Understand the core idea before remembering details.",
                    "A familiar example makes the idea easier to apply.",
                    "Explaining the idea yourself is a useful understanding check.",
                ],
                "check_question": f"How would you explain the main idea of {subject} using your own simple example?",
            }
        if profile == "telugu_assisted_english":
            return {
                "title": f"{subject} ముఖ్య భావనను అర్థం చేసుకుందాం",
                "introduction": f"ఈ పాఠంలో {subject} లోని ముఖ్యమైన concept ను సులభమైన తెలుగులో దశలవారీగా అర్థం చేసుకుందాం.",
                "explanation_steps": [
                    f"మొదట {subject} లోని core idea ఏమిటో సులభమైన మాటల్లో గుర్తించాలి.",
                    "తర్వాత ఆ భావనను మన రోజువారీ జీవితంలోని తెలిసిన ఉదాహరణతో కలిపి చూడాలి.",
                    "చివరగా example ను పరిశీలించి, భావనను మన సొంత మాటల్లో చెప్పాలి.",
                ],
                "example": f"{subject} కు సంబంధించిన ఒక చిన్న ఉదాహరణను ఊహించి, ఈ ప్రశ్నతో కలపండి: {request.student_question}",
                "key_points": [
                    "వివరాల కంటే ముందు main concept ను అర్థం చేసుకోవాలి.",
                    "సులభమైన example భావనను గుర్తుంచుకోవడానికి సహాయపడుతుంది.",
                    "మన సొంత మాటల్లో చెప్పడం understanding ను పరీక్షిస్తుంది.",
                ],
                "check_question": f"{subject} లోని ముఖ్య భావనను ఒక సులభమైన ఉదాహరణతో ఎలా వివరిస్తావు?",
            }
        return {
            "title": f"{subject} పునాది భావనను అర్థం చేసుకుందాం",
            "introduction": f"ఈ పాఠంలో {subject} లోని ముఖ్యమైన భావనను సులభమైన తెలుగులో, ఒక్కో దశగా అర్థం చేసుకుందాం.",
            "explanation_steps": [
                f"మొదట {subject} లోని ప్రధాన భావన ఏమిటో సులభమైన మాటల్లో తెలుసుకోవాలి.",
                "తర్వాత ఆ భావనకు మన రోజువారీ జీవితంలో కనిపించే సందర్భంతో సంబంధం కలపాలి.",
                "చివరగా చిన్న ఉదాహరణను పరిశీలించి, నేర్చుకున్న విషయాన్ని మన సొంత మాటల్లో చెప్పాలి.",
            ],
            "example": f"{subject} కు సంబంధించిన ఒక సాధారణ సందర్భాన్ని ఊహించుకో. దానిని ఈ ప్రశ్నతో కలిపి ఆలోచించు: {request.student_question}",
            "key_points": [
                "ముందుగా ప్రధాన భావనను స్పష్టంగా అర్థం చేసుకోవాలి.",
                "తెలిసిన ఉదాహరణతో పోల్చితే కొత్త విషయం సులభంగా అర్థమవుతుంది.",
                "సొంత మాటల్లో వివరించడం ద్వారా అవగాహనను పరీక్షించుకోవచ్చు.",
            ],
            "check_question": f"{subject} లోని ప్రధాన భావనను నీ సొంత ఉదాహరణతో ఎలా వివరిస్తావు?",
        }
