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
        concept_content = self._build_demo_concept_content(profile, request)
        if concept_content is not None:
            return concept_content
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
    def _build_demo_concept_content(
        profile: str,
        request: LessonGenerationRequest,
    ) -> dict[str, str | list[str]] | None:
        """Return concept-aligned recovery lessons for every approved demo concept."""

        lessons = {
            "fractions": {
                "title_en": "Fractions: equal parts of a whole",
                "title_te": "భిన్నాలు: మొత్తంలోని సమాన భాగాలు",
                "intro_en": "A fraction shows one or more equal parts of a whole. In 3/4, 3 is the numerator and 4 is the denominator.",
                "intro_te": "భిన్నం అనేది ఒక మొత్తాన్ని సమాన భాగాలుగా విభజించినప్పుడు వాటిలో ఎన్ని భాగాలు తీసుకున్నామో చూపుతుంది. 3/4లో 3 లవం, 4 హారం.",
                "steps_en": ["Divide one whole into equal parts.", "The denominator tells the total number of equal parts.", "The numerator tells how many of those parts are selected."],
                "steps_te": ["ఒక మొత్తాన్ని సమాన భాగాలుగా విభజించాలి.", "హారం మొత్తం సమాన భాగాల సంఖ్యను తెలియజేస్తుంది.", "లవం తీసుకున్న భాగాల సంఖ్యను తెలియజేస్తుంది."],
                "example_en": "A roti cut into 4 equal pieces has four quarters. Taking 3 pieces represents 3/4.",
                "example_te": "ఒక రొట్టెను 4 సమాన ముక్కలుగా కోసి, వాటిలో 3 ముక్కలు తీసుకుంటే అది 3/4.",
                "points_en": ["Parts must be equal.", "The numerator is written above the fraction bar.", "The denominator is written below the fraction bar."],
                "points_te": ["భాగాలు సమానంగా ఉండాలి.", "లవం భిన్న రేఖకు పైన ఉంటుంది.", "హారం భిన్న రేఖకు కింద ఉంటుంది."],
                "check_en": "A fruit is divided into 8 equal pieces and 3 are taken. Which fraction represents the taken pieces?",
                "check_te": "ఒక పండును 8 సమాన ముక్కలుగా చేసి 3 ముక్కలు తీసుకుంటే, తీసుకున్న భాగాన్ని ఏ భిన్నం సూచిస్తుంది?",
            },
            "decimals": {
                "title_en": "Decimals and place value",
                "title_te": "దశాంశాలు మరియు స్థాన విలువ",
                "intro_en": "Decimals represent whole numbers and parts smaller than one using a decimal point.",
                "intro_te": "దశాంశ బిందువును ఉపయోగించి పూర్ణ సంఖ్యలతో పాటు ఒకటి కంటే చిన్న భాగాలను దశాంశాలు సూచిస్తాయి.",
                "steps_en": ["Digits left of the decimal point represent whole-number places.", "The first place to the right is tenths.", "The second place to the right is hundredths."],
                "steps_te": ["దశాంశ బిందువు ఎడమవైపు అంకెలు పూర్ణ సంఖ్య స్థానాలను సూచిస్తాయి.", "కుడివైపు మొదటి స్థానం పదవ వంతులను సూచిస్తుంది.", "కుడివైపు రెండవ స్థానం నూరవ వంతులను సూచిస్తుంది."],
                "example_en": "In 2.35, 2 is the whole-number part, 3 means three tenths, and 5 means five hundredths.",
                "example_te": "2.35లో 2 పూర్ణ సంఖ్య, 3 మూడు పదవ వంతులు, 5 ఐదు నూరవ వంతులను సూచిస్తాయి.",
                "points_en": ["Place value changes across the decimal point.", "Align decimal points when comparing numbers.", "0.5 is the same as 0.50."],
                "points_te": ["దశాంశ బిందువు ఆధారంగా స్థాన విలువ మారుతుంది.", "సంఖ్యలను పోల్చేటప్పుడు దశాంశ బిందువులను ఒకే వరుసలో ఉంచాలి.", "0.5 మరియు 0.50 సమాన విలువలు."],
                "check_en": "What is the value of 7 in 4.72?",
                "check_te": "4.72లో 7 యొక్క స్థాన విలువ ఎంత?",
            },
            "solar system": {
                "title_en": "Our Solar System",
                "title_te": "మన సౌర కుటుంబం",
                "intro_en": "The Solar System consists of the Sun and the planets, moons, asteroids, and comets held by its gravity.",
                "intro_te": "సూర్యుడు, అతని గురుత్వాకర్షణ వల్ల కక్ష్యల్లో తిరిగే గ్రహాలు, ఉపగ్రహాలు, గ్రహశకలాలు, తోకచుక్కలు కలిసి సౌర కుటుంబాన్ని ఏర్పరుస్తాయి.",
                "steps_en": ["The Sun is a star at the centre of the Solar System.", "Eight planets orbit the Sun in paths called orbits.", "Earth rotates on its axis and revolves around the Sun."],
                "steps_te": ["సూర్యుడు సౌర కుటుంబం మధ్యలో ఉన్న ఒక నక్షత్రం.", "ఎనిమిది గ్రహాలు కక్ష్యలు అనే మార్గాల్లో సూర్యుని చుట్టూ తిరుగుతాయి.", "భూమి తన అక్షంపై తిరుగుతూ సూర్యుని చుట్టూ పరిభ్రమిస్తుంది."],
                "example_en": "Earth takes about one year to complete one revolution around the Sun.",
                "example_te": "భూమి సూర్యుని చుట్టూ ఒకసారి పరిభ్రమించడానికి సుమారు ఒక సంవత్సరం పడుతుంది.",
                "points_en": ["The Sun supplies light and heat.", "Planets do not produce their own light.", "Gravity keeps objects in orbit."],
                "points_te": ["సూర్యుడు కాంతి, వేడిని అందిస్తాడు.", "గ్రహాలు స్వంత కాంతిని ఉత్పత్తి చేయవు.", "గురుత్వాకర్షణ ఖగోళ వస్తువులను కక్ష్యల్లో ఉంచుతుంది."],
                "check_en": "Why does Earth remain in orbit around the Sun?",
                "check_te": "భూమి సూర్యుని చుట్టూ కక్ష్యలో ఎందుకు ఉంటుంది?",
            },
            "water cycle": {
                "title_en": "The Water Cycle",
                "title_te": "నీటి చక్రం",
                "intro_en": "The water cycle is the continuous movement of water between Earth's surface and the atmosphere.",
                "intro_te": "భూమి ఉపరితలం మరియు వాతావరణం మధ్య నీరు నిరంతరం మారుతూ ప్రయాణించే ప్రక్రియను నీటి చక్రం అంటారు.",
                "steps_en": ["Sunlight heats water and causes evaporation.", "Water vapour cools and condenses into clouds.", "Water returns as rain or other precipitation and collects again."],
                "steps_te": ["సూర్యుడి వేడి వల్ల నీరు ఆవిరవుతుంది.", "నీటి ఆవిరి చల్లబడి చిన్న బిందువులుగా మారి మేఘాలను ఏర్పరుస్తుంది.", "వర్షపాతం ద్వారా నీరు భూమికి తిరిగి వచ్చి మళ్లీ జలాశయాల్లో చేరుతుంది."],
                "example_en": "A puddle becomes smaller in sunlight because its water evaporates and enters the air.",
                "example_te": "ఎండలో నీటి మడుగు చిన్నదవుతుంది; అందులోని నీరు ఆవిరై గాలిలో కలుస్తుంది.",
                "points_en": ["Evaporation changes liquid water to vapour.", "Condensation forms cloud droplets.", "Precipitation returns water to Earth."],
                "points_te": ["ఆవిరీకరణలో ద్రవ నీరు ఆవిరిగా మారుతుంది.", "సంఘననంతో మేఘ బిందువులు ఏర్పడతాయి.", "వర్షపాతం నీటిని భూమికి తిరిగి తీసుకువస్తుంది."],
                "check_en": "What happens to water vapour when it cools?",
                "check_te": "నీటి ఆవిరి చల్లబడినప్పుడు ఏమవుతుంది?",
            },
            "photosynthesis": {
                "title_en": "Photosynthesis: how plants make food",
                "title_te": "కిరణజన్య సంయోగక్రియ: మొక్కలు ఆహారం తయారు చేసుకునే విధానం",
                "intro_en": "Photosynthesis is the process by which green plants use sunlight, water, and carbon dioxide to make food and release oxygen.",
                "intro_te": "ఆకుపచ్చ మొక్కలు సూర్యకాంతి, నీరు, కార్బన్ డయాక్సైడ్‌ను ఉపయోగించి ఆహారం తయారు చేసి ఆక్సిజన్ విడుదల చేసే ప్రక్రియను కిరణజన్య సంయోగక్రియ అంటారు.",
                "steps_en": ["Roots absorb water from the soil.", "Leaves take in carbon dioxide and capture sunlight using chlorophyll.", "The plant makes glucose and releases oxygen."],
                "steps_te": ["వేర్లు నేల నుండి నీటిని గ్రహిస్తాయి.", "ఆకులు కార్బన్ డయాక్సైడ్‌ను తీసుకుని పత్రహరితం సహాయంతో సూర్యకాంతిని గ్రహిస్తాయి.", "మొక్క గ్లూకోజ్ అనే ఆహారాన్ని తయారు చేసి ఆక్సిజన్‌ను విడుదల చేస్తుంది."],
                "example_en": "A plant kept without light becomes weak because it cannot photosynthesise normally.",
                "example_te": "కాంతి లేకుండా ఉంచిన మొక్క సాధారణంగా కిరణజన్య సంయోగక్రియ చేయలేక బలహీనమవుతుంది.",
                "points_en": ["Sunlight provides energy.", "Leaves are the main food-making organs.", "Oxygen is released during the process."],
                "points_te": ["సూర్యకాంతి శక్తిని అందిస్తుంది.", "ఆకులు ప్రధానంగా ఆహారం తయారు చేస్తాయి.", "ఈ ప్రక్రియలో ఆక్సిజన్ విడుదలవుతుంది."],
                "check_en": "Which three main inputs does a plant need for photosynthesis?",
                "check_te": "కిరణజన్య సంయోగక్రియకు మొక్కకు అవసరమైన మూడు ప్రధాన పదార్థాలు ఏవి?",
            },
            "grammar": {
                "title_en": "English Grammar: building clear sentences",
                "title_te": "ఆంగ్ల వ్యాకరణం: స్పష్టమైన వాక్యాల నిర్మాణం",
                "intro_en": "Grammar is the set of rules that helps us arrange words into clear and meaningful sentences.",
                "intro_te": "పదాలను స్పష్టమైన, అర్థవంతమైన వాక్యాలుగా అమర్చడానికి సహాయపడే నియమాల సమాహారమే ఆంగ్ల వ్యాకరణం.",
                "steps_en": ["Identify who or what the sentence is about.", "Choose a verb that shows the action or state.", "Add necessary details and check word order and punctuation."],
                "steps_te": ["వాక్యం ఎవరి గురించి లేదా దేని గురించి చెబుతుందో గుర్తించాలి.", "చర్య లేదా స్థితిని తెలిపే క్రియను ఎంచుకోవాలి.", "అవసరమైన వివరాలు జోడించి పదక్రమం, విరామచిహ్నాలను తనిఖీ చేయాలి."],
                "example_en": "In “Ravi reads a book,” Ravi is the subject, reads is the verb, and a book completes the idea.",
                "example_te": "“Ravi reads a book” అనే వాక్యంలో Ravi కర్త, reads క్రియ, a book వాక్య భావాన్ని పూర్తి చేస్తుంది.",
                "points_en": ["A complete sentence expresses a complete thought.", "The subject and verb must agree.", "Punctuation helps readers understand meaning."],
                "points_te": ["పూర్తి వాక్యం సంపూర్ణ భావాన్ని తెలియజేస్తుంది.", "కర్త, క్రియ ఒకదానికొకటి సరిపోవాలి.", "విరామచిహ్నాలు భావాన్ని స్పష్టంగా తెలియజేస్తాయి."],
                "check_en": "Identify the subject and verb in: “The children play outside.”",
                "check_te": "“The children play outside” అనే వాక్యంలో కర్త, క్రియలను గుర్తించండి.",
            },
            "telugu grammar": {
                "title_en": "Telugu Grammar: sentence structure",
                "title_te": "తెలుగు వ్యాకరణం: వాక్య నిర్మాణం",
                "intro_en": "Telugu grammar explains how words change and combine to create meaningful Telugu sentences.",
                "intro_te": "పదాలు ఎలా రూపాంతరం చెంది, పరస్పరం కలిసి అర్థవంతమైన తెలుగు వాక్యాలను నిర్మిస్తాయో తెలుగు వ్యాకరణం వివరిస్తుంది.",
                "steps_en": ["Identify the subject of the sentence.", "Identify the object or additional information.", "Place the verb naturally at the end in a common Telugu sentence."],
                "steps_te": ["వాక్యంలోని కర్తను గుర్తించాలి.", "కర్మను లేదా అదనపు సమాచారాన్ని గుర్తించాలి.", "సాధారణ తెలుగు వాక్యంలో క్రియను సహజంగా చివర ఉంచాలి."],
                "example_en": "“రాము పుస్తకం చదివాడు” contains the subject రాము, object పుస్తకం, and verb చదివాడు.",
                "example_te": "“రాము పుస్తకం చదివాడు” అనే వాక్యంలో రాము కర్త, పుస్తకం కర్మ, చదివాడు క్రియ.",
                "points_en": ["Word forms show number, gender, tense, and relation.", "Correct word order makes meaning clear.", "The verb often appears at the end."],
                "points_te": ["పదరూపాలు వచనం, లింగం, కాలం, సంబంధాన్ని తెలియజేస్తాయి.", "సరైన పదక్రమం భావాన్ని స్పష్టంగా చేస్తుంది.", "క్రియ సాధారణంగా వాక్యం చివర ఉంటుంది."],
                "check_en": "Identify the subject and verb in “సీత పాట పాడింది”.",
                "check_te": "“సీత పాట పాడింది” అనే వాక్యంలో కర్త, క్రియలను గుర్తించండి.",
            },
        }
        topic = lessons.get(request.concept.casefold())
        if topic is None:
            return None
        if profile == "english_medium":
            suffix = "en"
        elif profile == "pure_telugu":
            suffix = "te"
        else:
            suffix = "te"
        return {
            "title": topic[f"title_{suffix}"],
            "introduction": topic[f"intro_{suffix}"],
            "explanation_steps": topic[f"steps_{suffix}"],
            "example": topic[f"example_{suffix}"],
            "key_points": topic[f"points_{suffix}"],
            "check_question": topic[f"check_{suffix}"],
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
