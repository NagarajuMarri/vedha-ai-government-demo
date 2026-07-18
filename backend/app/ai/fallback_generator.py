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
        if request.subject == "Social Studies":
            return self._build_social_studies_content(profile, request)
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


    @staticmethod
    def _build_social_studies_content(
        profile: str,
        request: LessonGenerationRequest,
    ) -> dict[str, str | list[str]]:
        """Return concept-specific Social Studies recovery content in the selected language."""

        topics = {
            "indian constitution": {
                "en": "The Indian Constitution is the supreme law of India. It defines citizens' rights and duties, the powers of government institutions, and the rules by which the country is governed.",
                "te": "భారత రాజ్యాంగం దేశంలోని అత్యున్నత చట్టం. ఇది పౌరుల హక్కులు, బాధ్యతలు, ప్రభుత్వ సంస్థల అధికారాలు, దేశ పాలనా నియమాలను వివరిస్తుంది.",
                "example_en": "The right to equality means that the law must treat citizens equally and cannot discriminate without a lawful reason.",
                "example_te": "సమానత్వ హక్కు ప్రకారం చట్టం పౌరులందరినీ సమానంగా చూడాలి; సరైన చట్టపరమైన కారణం లేకుండా వివక్ష చూపకూడదు.",
                "check_en": "Name one Fundamental Right and explain why it is important in daily life.",
                "check_te": "ఒక ప్రాథమిక హక్కును పేర్కొని, అది రోజువారీ జీవితంలో ఎందుకు ముఖ్యమో వివరించండి.",
            },
            "indian freedom movement": {
                "en": "The Indian Freedom Movement was a long struggle against British colonial rule. People used public movements, boycotts, writing, negotiation, and sacrifice to seek self-rule, leading to independence in 1947.",
                "te": "భారత స్వాతంత్ర్య ఉద్యమం బ్రిటిష్ వలస పాలనకు వ్యతిరేకంగా జరిగిన దీర్ఘ పోరాటం. ప్రజా ఉద్యమాలు, బహిష్కరణలు, రచనలు, చర్చలు, త్యాగాల ద్వారా స్వపరిపాలన కోసం పోరాడి 1947లో స్వాతంత్ర్యం సాధించారు.",
                "example_en": "The Salt March showed how an everyday item such as salt could become a symbol of resistance to an unjust colonial law.",
                "example_te": "ఉప్పు సత్యాగ్రహం ద్వారా రోజువారీ అవసరమైన ఉప్పు కూడా అన్యాయమైన వలస చట్టానికి వ్యతిరేక ప్రతిఘటనకు చిహ్నంగా మారింది.",
                "check_en": "How did mass participation strengthen India's freedom movement?",
                "check_te": "ప్రజల విస్తృత భాగస్వామ్యం భారత స్వాతంత్ర్య ఉద్యమాన్ని ఎలా బలపరిచింది?",
            },
            "andhra pradesh geography": {
                "en": "Andhra Pradesh has a long Bay of Bengal coastline, the Eastern Ghats, fertile river plains, and varied dry and coastal regions. The Krishna and Godavari rivers strongly influence farming, settlements, and livelihoods.",
                "te": "ఆంధ్రప్రదేశ్‌కు పొడవైన బంగాళాఖాత తీరరేఖ, తూర్పు కనుమలు, సారవంతమైన నదీ మైదానాలు, తీర మరియు పొడి ప్రాంతాలు ఉన్నాయి. కృష్ణా, గోదావరి నదులు వ్యవసాయం, నివాసాలు, జీవనోపాధులపై గొప్ప ప్రభావం చూపుతాయి.",
                "example_en": "The Godavari delta supports intensive agriculture because river water and deposited soil make the plains fertile.",
                "example_te": "గోదావరి డెల్టాలో నదీ జలం, నది తెచ్చే మట్టి కారణంగా మైదానాలు సారవంతమై విస్తృత వ్యవసాయానికి అనుకూలంగా ఉంటాయి.",
                "check_en": "How do the Krishna and Godavari rivers affect life in Andhra Pradesh?",
                "check_te": "కృష్ణా, గోదావరి నదులు ఆంధ్రప్రదేశ్ ప్రజల జీవనంపై ఎలా ప్రభావం చూపుతాయి?",
            },
            "local government": {
                "en": "Local government manages community needs close to where people live. Gram Panchayats serve villages, while Municipalities and Municipal Corporations serve towns and cities through elected representatives.",
                "te": "స్థానిక ప్రభుత్వం ప్రజలు నివసించే ప్రాంతానికి సమీపంగా సామాజిక అవసరాలను నిర్వహిస్తుంది. గ్రామాలకు గ్రామ పంచాయతీలు, పట్టణాలు మరియు నగరాలకు పురపాలక సంఘాలు, నగరపాలక సంస్థలు ఎన్నికైన ప్రతినిధుల ద్వారా సేవలు అందిస్తాయి.",
                "example_en": "Repairing a village road, maintaining streetlights, and arranging local sanitation are matters commonly handled by local bodies.",
                "example_te": "గ్రామ రహదారి మరమ్మతు, వీధి దీపాల నిర్వహణ, పారిశుద్ధ్య ఏర్పాట్లు సాధారణంగా స్థానిక సంస్థలు నిర్వహించే పనులు.",
                "check_en": "Which local body serves your area, and name one service it provides.",
                "check_te": "మీ ప్రాంతానికి సేవలందించే స్థానిక సంస్థ ఏది? అది అందించే ఒక సేవను పేర్కొనండి.",
            },
            "climate and natural resources": {
                "en": "Climate influences rainfall, crops, water availability, and daily life. Natural resources such as soil, water, forests, and minerals must be used carefully so they remain available for future generations.",
                "te": "వాతావరణం వర్షపాతం, పంటలు, నీటి లభ్యత, రోజువారీ జీవితాన్ని ప్రభావితం చేస్తుంది. నేల, నీరు, అడవులు, ఖనిజాలు వంటి సహజ వనరులను భవిష్యత్ తరాలకు అందుబాటులో ఉండేలా జాగ్రత్తగా వినియోగించాలి.",
                "example_en": "Collecting rainwater can reduce pressure on groundwater and help communities during dry months.",
                "example_te": "వర్షపు నీటిని సేకరించడం వల్ల భూగర్భ జలాలపై ఒత్తిడి తగ్గి, ఎండాకాలంలో సమాజానికి ఉపయోగపడుతుంది.",
                "check_en": "Suggest one way your school or home can conserve a natural resource.",
                "check_te": "మీ పాఠశాల లేదా ఇంటిలో ఒక సహజ వనరును సంరక్షించడానికి ఒక మార్గాన్ని సూచించండి.",
            },
        }
        topic = topics.get(request.concept.casefold(), topics["indian constitution"])
        if profile == "english_medium":
            return {
                "title": request.concept,
                "introduction": topic["en"],
                "explanation_steps": [
                    f"Define {request.concept} and identify whether it belongs mainly to history, geography, or civics.",
                    topic["en"],
                    "Connect the idea to the people, places, institutions, dates, or natural features that shape it.",
                    "Study its causes or structure, then examine its effects on society and everyday life.",
                    "Use evidence and the example below to explain the concept in your own words.",
                ],
                "example": topic["example_en"],
                "key_points": [
                    f"{request.concept} is a specific Social Studies concept, not only a broad subject heading.",
                    "People, places, institutions, evidence, and cause-and-effect help us understand Social Studies.",
                    "Connecting the concept to India and Andhra Pradesh makes it meaningful.",
                ],
                "check_question": topic["check_en"],
            }
        if profile == "telugu_assisted_english":
            return {
                "title": f"{request.concept} · సామాజిక శాస్త్రం",
                "introduction": topic["te"],
                "explanation_steps": [
                    f"మొదట {request.concept} అనేది history, geography లేదా civicsలో దేనికి సంబంధించినదో గుర్తించాలి.",
                    topic["te"],
                    "దీనికి సంబంధించిన people, places, institutions లేదా natural featuresను గుర్తించాలి.",
                    "కారణాలు లేదా నిర్మాణాన్ని తెలుసుకుని, society మరియు daily lifeపై ప్రభావాలను పరిశీలించాలి.",
                    "క్రింది example ఆధారంగా conceptను సొంత మాటల్లో వివరించాలి.",
                ],
                "example": topic["example_te"],
                "key_points": [
                    "ప్రశ్నలో ఎంచుకున్న conceptకే explanation నేరుగా సంబంధించినది కావాలి.",
                    "People, places, institutions, evidence, cause-and-effect ముఖ్యమైనవి.",
                    "India మరియు Andhra Pradesh contextతో అనుసంధానం understandingను పెంచుతుంది.",
                ],
                "check_question": topic["check_te"],
            }
        telugu_titles = {
            "indian constitution": "భారత రాజ్యాంగం",
            "indian freedom movement": "భారత స్వాతంత్ర్య ఉద్యమం",
            "andhra pradesh geography": "ఆంధ్రప్రదేశ్ భూగోళ శాస్త్రం",
            "local government": "స్థానిక ప్రభుత్వం",
            "climate and natural resources": "వాతావరణం మరియు సహజ వనరులు",
        }
        return {
            "title": telugu_titles.get(request.concept.casefold(), "సామాజిక శాస్త్ర పాఠం"),
            "introduction": topic["te"],
            "explanation_steps": [
                "మొదట ఈ అంశం చరిత్ర, భూగోళ శాస్త్రం లేదా పౌర శాస్త్రంలో దేనికి సంబంధించినదో గుర్తించాలి.",
                topic["te"],
                "దీనికి సంబంధించిన ప్రజలు, ప్రదేశాలు, సంస్థలు, కాలం లేదా సహజ లక్షణాలను గుర్తించాలి.",
                "దాని కారణాలు లేదా నిర్మాణాన్ని తెలుసుకుని, సమాజం మరియు రోజువారీ జీవితంపై ప్రభావాలను పరిశీలించాలి.",
                "క్రింది ఉదాహరణ, ఆధారాల సహాయంతో అంశాన్ని సొంత మాటల్లో వివరించాలి.",
            ],
            "example": topic["example_te"],
            "key_points": [
                "ఎంచుకున్న అంశాన్నే నేరుగా అర్థం చేసుకోవాలి.",
                "ప్రజలు, ప్రదేశాలు, సంస్థలు, ఆధారాలు, కారణాలు మరియు ఫలితాలు సామాజిక శాస్త్రంలో ముఖ్యమైనవి.",
                "భారతదేశం, ఆంధ్రప్రదేశ్ సందర్భాలతో అనుసంధానం చేస్తే విషయం స్పష్టమవుతుంది.",
            ],
            "check_question": topic["check_te"],
        }
