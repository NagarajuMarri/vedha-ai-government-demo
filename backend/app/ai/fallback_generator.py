"""Deterministic fallback lesson generator for approved recoverable failures."""

from __future__ import annotations

from backend.app.ai.lesson_models import LessonGenerationRequest, LessonResult
from backend.app.ai.language_profiles import localize_subject
from backend.app.ai.prompt_registry import get_active_prompt


class DeterministicFallbackLessonGenerator:
    """Provide safe, provider-independent fallback lesson content."""

    def generate(self, request: LessonGenerationRequest) -> LessonResult:
        """Create deterministic fallback output from the normalized request."""

        profile = request.learning_profile
        content = self._build_content(profile, request)
        prompt = get_active_prompt(request.subject, profile)

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
            prompt_id=prompt.prompt_id,
            prompt_version=prompt.prompt_version,
        )

    def _build_content(self, profile: str, request: LessonGenerationRequest) -> dict[str, str | list[str]]:
        subject = localize_subject(request.subject, profile)
        concept = request.concept.casefold()
        if profile == "pure_telugu" and concept == "geometry":
            return {
                "title": "జ్యామితి: బిందువులు, రేఖలు, కోణాలు",
                "introduction": "జ్యామితి అనేది ఆకారాలు, పరిమాణాలు, స్థానాలు మరియు వాటి మధ్య సంబంధాలను అధ్యయనం చేసే గణిత విభాగం.",
                "explanation_steps": [
                    "బిందువు ఒక ఖచ్చితమైన స్థానాన్ని సూచిస్తుంది; దానికి పొడవు లేదా వెడల్పు ఉండదు.",
                    "రేఖ రెండు దిశల్లో కొనసాగుతుంది; రేఖాఖండానికి రెండు చివరి బిందువులు ఉంటాయి.",
                    "ఒకే బిందువు నుండి బయలుదేరే రెండు కిరణాల మధ్య ఏర్పడే విస్తారాన్ని కోణం అంటారు.",
                    "మూడు రేఖాఖండాలతో ఏర్పడే మూసిన ఆకారాన్ని త్రిభుజం అంటారు; దాని అంతర్గత కోణాల మొత్తం 180°.",
                ],
                "example": "ఒక త్రిభుజంలోని రెండు కోణాలు 50° మరియు 60° అయితే, మూడవ కోణం 180° − 50° − 60° = 70°.",
                "key_points": [
                    "బిందువు స్థానాన్ని సూచిస్తుంది.",
                    "రేఖాఖండానికి రెండు చివరి బిందువులు ఉంటాయి.",
                    "కోణాన్ని డిగ్రీలలో కొలుస్తారు.",
                    "త్రిభుజంలోని కోణాల మొత్తం 180°.",
                ],
                "check_question": "ఒక త్రిభుజంలోని రెండు కోణాలు 40° మరియు 80° అయితే మూడవ కోణం ఎంత?",
            }
        if profile == "telugu_assisted_english" and concept == "geometry":
            return {
                "title": "Geometry: బిందువులు, రేఖలు మరియు కోణాలు",
                "introduction": "Geometryలో shapes, sizes, positions మరియు వాటి relationshipsను అధ్యయనం చేస్తాము.",
                "explanation_steps": [
                    "Point ఒక exact positionను సూచిస్తుంది.",
                    "Line రెండు directionsలో కొనసాగుతుంది; line segmentకు రెండు end points ఉంటాయి.",
                    "ఒకే point నుండి వచ్చే రెండు rays మధ్య ఏర్పడేది angle.",
                    "Triangle మూడు line segmentsతో ఏర్పడుతుంది; interior angles మొత్తం 180°.",
                ],
                "example": "Triangleలో రెండు angles 50° మరియు 60° అయితే, third angle = 180° − 50° − 60° = 70°.",
                "key_points": ["Point స్థానాన్ని చూపుతుంది.", "Angleను degreesలో కొలుస్తారు.", "Triangle angles మొత్తం 180°."],
                "check_question": "Triangleలో రెండు angles 40° మరియు 80° అయితే third angle ఎంత?",
            }
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
