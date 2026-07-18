"""Sprint 4A OpenAI integration, prompt policy, and fallback tests."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace

import httpx
import pytest

from backend.app.ai.exceptions import (
    AIAuthenticationError,
    AIConfigurationError,
    AIInsufficientQuotaError,
    AIInvalidResponseError,
    AIModelNotFoundError,
    AIProviderUnavailableError,
    AIRateLimitError,
    AIRefusalError,
    AIReviewerRejectionError,
    AITimeoutError,
)
from backend.app.ai.fallback_generator import DeterministicFallbackLessonGenerator
from backend.app.ai.language_profiles import localize_subject
from backend.app.ai.lesson_models import GeneratedLessonContent, LessonGenerationRequest, LessonResult
from backend.app.ai.prompt_builder import LessonPromptBuilder
from backend.app.ai.prompt_registry import PROMPT_REGISTRY, get_active_prompt
from backend.app.ai.providers.base import LessonProvider
from backend.app.ai.providers.openai_provider import OpenAIProvider
from backend.app.ai.services.lesson_service import LessonGenerationService
from backend.app.ai.services.lesson_reviewer import LessonReviewer
from backend.app.api.lessons import _get_service
from backend.app.core.config import Settings, get_safe_ai_configuration
from backend.app.main import create_app


def _settings(**overrides: object) -> Settings:
    values = {
        "project_name": "Vedha AI Government Demo",
        "environment": "test",
        "api_v1_prefix": "/api/v1",
        "log_level": "INFO",
        "cors_origins": ("http://127.0.0.1:8080",),
        "openai_api_key": "unit-test-key",
        "openai_model": "configured-test-model",
        "openai_timeout_seconds": 30,
        "ai_provider": "openai",
        "ai_fallback_enabled": True,
    }
    values.update(overrides)
    return Settings(**values)


def _request(profile: str = "english_medium", subject: str = "Mathematics") -> LessonGenerationRequest:
    question = "భిన్నం అంటే ఏమిటి?" if profile == "pure_telugu" else "What is a fraction?"
    return LessonGenerationRequest(
        class_level="5",
        subject=subject,
        learning_profile=profile,
        student_question=question,
    )


def _content(**overrides: object) -> GeneratedLessonContent:
    values = {
        "title": "Understanding fractions clearly",
        "introduction": "A fraction represents one or more equal parts of a whole object.",
        "explanation_steps": ["Divide a whole into equal parts.", "Count the selected equal parts."],
        "example": "One of four equal pieces of fruit represents the fraction one-fourth.",
        "key_points": ["Parts must be equal.", "The whole determines the fraction."],
        "check_question": "What fraction is one piece out of four equal pieces?",
        "learning_profile": "english_medium",
        "subject": "Mathematics",
        "class_level": "5",
    }
    values.update(overrides)
    return GeneratedLessonContent(**values)


def test_prompt_registry_has_all_active_versioned_subject_prompts() -> None:
    expected = {
        "vedha_general_teacher_v1",
        "vedha_mathematics_teacher_v1",
        "vedha_science_teacher_v1",
        "vedha_english_teacher_v1",
        "vedha_telugu_teacher_v1",
        "vedha_social_studies_teacher_v1",
    }
    assert {prompt.prompt_id for prompt in PROMPT_REGISTRY} == expected
    versions = {prompt.prompt_id: prompt.prompt_version for prompt in PROMPT_REGISTRY}
    assert all(prompt.active for prompt in PROMPT_REGISTRY)
    assert versions["vedha_mathematics_teacher_v1"] == "1.1.0"
    assert all(version == "1.0.0" for prompt_id, version in versions.items() if prompt_id != "vedha_mathematics_teacher_v1")


@pytest.mark.parametrize(
    ("subject", "prompt_id", "rule"),
    [
        ("Mathematics", "vedha_mathematics_teacher_v1", "numerator above"),
        ("Science", "vedha_science_teacher_v1", "observable phenomena"),
        ("English", "vedha_english_teacher_v1", "grammar, vocabulary"),
        ("Telugu", "vedha_telugu_teacher_v1", "correct Telugu grammar"),
        ("Social Studies", "vedha_social_studies_teacher_v1", "historical fact"),
    ],
)
def test_registry_selects_subject_prompt_and_rules(subject: str, prompt_id: str, rule: str) -> None:
    definition = get_active_prompt(subject, "english_medium")
    assert definition.prompt_id == prompt_id
    assert rule.lower() in " ".join(definition.teaching_rules).lower()


@pytest.mark.parametrize(
    ("profile", "required"),
    [
        ("english_medium", "English academic and technical terminology"),
        ("telugu_assisted_english", "Explanation primarily in Telugu"),
        ("pure_telugu", "established Telugu educational terminology"),
    ],
)
def test_prompt_contains_profile_policy(profile: str, required: str) -> None:
    prompt = LessonPromptBuilder().build_request(
        class_level="5",
        subject="Mathematics",
        learning_profile=profile,
        student_question="Explain a fraction simply.",
    )
    assert required in prompt.instructions
    assert prompt.prompt_id == "vedha_mathematics_teacher_v1"
    assert prompt.prompt_version == "1.1.0"
    assert "Explain a fraction simply." not in prompt.instructions
    assert "Explain a fraction simply." in prompt.student_input


def test_pure_telugu_subject_and_mathematics_terms_are_policy_localized() -> None:
    assert localize_subject("Mathematics", "pure_telugu") == "గణితం"
    prompt = LessonPromptBuilder().build_request(
        class_level="5",
        subject="Mathematics",
        learning_profile="pure_telugu",
        student_question="భిన్నం అంటే ఏమిటి?",
    )
    for term in ("భిన్నం", "లవం", "హారం", "కనిష్ఠ సామాన్య గుణిజం", "గరిష్ఠ సామాన్య కారణాంకం"):
        assert term in prompt.instructions


def test_openai_provider_uses_configured_sdk_values_and_strict_typed_parse(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeResponses:
        def parse(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(output_parsed=_content(), output=[])

    class FakeClient:
        def __init__(self, **kwargs):
            captured["client_api_key"] = kwargs["api_key"]
            captured["client_timeout"] = kwargs["timeout"]
            captured["max_retries"] = kwargs["max_retries"]
            self.responses = FakeResponses()

    monkeypatch.setattr("backend.app.ai.providers.openai_provider.OpenAI", FakeClient)
    result = OpenAIProvider(_settings()).generate_lesson(_request())

    assert captured["model"] == "configured-test-model"
    assert captured["client_api_key"] == "unit-test-key"
    assert captured["client_timeout"] == 30
    assert captured["max_retries"] == 0
    assert captured["text_format"] is GeneratedLessonContent
    assert captured["store"] is False
    assert result.source == "openai"
    assert result.fallback_used is False
    assert result.prompt_id == "vedha_mathematics_teacher_v1"
    assert result.prompt_version == "1.1.0"


def test_localized_model_metadata_cannot_override_canonical_request_metadata(monkeypatch) -> None:
    localized_content = GeneratedLessonContent(
        title="భిన్నాలను సులభంగా అర్థం చేసుకుందాం",
        introduction="భిన్నం అనేది ఒక మొత్తాన్ని సమాన భాగాలుగా విభజించినప్పుడు వచ్చే భాగాన్ని తెలియజేస్తుంది.",
        explanation_steps=[
            "మొదట ఒక మొత్తాన్ని సమాన భాగాలుగా విభజించాలి.",
            "లవం తీసుకున్న భాగాలను, హారం మొత్తం సమాన భాగాలను సూచిస్తాయి.",
        ],
        example="ఒక పండును నాలుగు సమాన భాగాలుగా చేసి ఒక భాగం తీసుకుంటే అది నాలుగవ వంతు.",
        key_points=[
            "భాగాలు తప్పనిసరిగా సమానంగా ఉండాలి.",
            "లవం మరియు హారం భిన్నంలోని ముఖ్య భాగాలు.",
        ],
        check_question="నాలుగు సమాన భాగాలలో ఒక భాగాన్ని ఏ భిన్నంతో సూచిస్తావు?",
        subject="గణితం",
        class_level="తరగతి 5",
        learning_profile="english_medium",
    )

    class FakeClient:
        def __init__(self, **kwargs):
            self.responses = SimpleNamespace(
                parse=lambda **call_kwargs: SimpleNamespace(
                    output_parsed=localized_content,
                    output=[],
                )
            )

    monkeypatch.setattr("backend.app.ai.providers.openai_provider.OpenAI", FakeClient)
    request = _request(profile="pure_telugu")
    provider = OpenAIProvider(_settings())
    provider_result = provider.generate_lesson(request)

    assert provider_result.subject == "Mathematics"
    assert provider_result.class_level == "5"
    assert provider_result.learning_profile == "pure_telugu"
    assert provider_result.source == "openai"
    assert provider_result.fallback_used is False
    assert "గణితం" in provider_result.title or "భిన్న" in provider_result.title

    service = LessonGenerationService(_settings(), provider=provider)
    reviewed_result = service.generate_lesson(request)
    assert reviewed_result.source == "openai"
    assert reviewed_result.fallback_used is False
    assert reviewed_result.subject == request.subject
    assert reviewed_result.class_level == request.class_level
    assert reviewed_result.learning_profile == request.learning_profile
    assert service.last_fallback_reason is None


def _pure_telugu_fraction_lesson(**updates: object) -> LessonResult:
    values: dict[str, object] = {
        "title": "భిన్నం, లవం మరియు హారం",
        "introduction": "ఒక మొత్తాన్ని సమాన భాగాలుగా విభజించినప్పుడు ప్రతి భాగాన్ని భిన్నంతో సూచించవచ్చు.",
        "explanation_steps": [
            "ఒక రొట్టెను ఎనిమిది సమాన భాగాలుగా చేసి ఆరు భాగాలు తీసుకుంటే దానిని 6/8గా రాస్తాము.",
            "6/8లో లవం 6. లవం భిన్న రేఖకు పైన ఉంటుంది.",
            "6/8లో హారం 8. హారం భిన్న రేఖకు కింద ఉంటుంది.",
        ],
        "example": "6/8 అంటే ఎనిమిదిలో ఆరు భాగాలు అని సహజంగా చదవవచ్చు.",
        "key_points": [
            "లవం తీసుకున్న సమాన భాగాల సంఖ్యను చూపుతుంది.",
            "హారం మొత్తంలోని సమాన భాగాల సంఖ్యను చూపుతుంది.",
        ],
        "check_question": "3/5లో లవం ఏది, హారం ఏది చెప్పగలవా?",
        "learning_profile": "pure_telugu",
        "subject": "Mathematics",
        "class_level": "5",
        "source": "openai",
        "fallback_used": False,
        "prompt_id": "vedha_mathematics_teacher_v1",
        "prompt_version": "1.1.0",
    }
    values.update(updates)
    return LessonResult(**values)


def _fraction_parts_request(question: str = "భిన్నాలు అంటే ఏమిటి? లవం మరియు హారం ఉదాహరణతో వివరించండి.") -> LessonGenerationRequest:
    return LessonGenerationRequest(
        class_level="5",
        subject="Mathematics",
        learning_profile="pure_telugu",
        student_question=question,
    )


def test_pure_telugu_reviewer_rejects_unexpected_chinese_script() -> None:
    lesson = _pure_telugu_fraction_lesson(
        introduction="భిన్నాన్ని 表示 చేసే ఈ వాక్యంలో అనుమతించని లిపి ఉంది.",
    )
    with pytest.raises(AIReviewerRejectionError) as exc_info:
        LessonReviewer().review(lesson, _fraction_parts_request())
    assert exc_info.value.validation_rule == "unexpected_script"


def test_natural_telugu_fraction_content_and_notation_pass_review() -> None:
    lesson = _pure_telugu_fraction_lesson()
    reviewed = LessonReviewer().review(lesson, _fraction_parts_request())
    assert reviewed == lesson
    assert "6/8" in reviewed.example
    assert "లవం" in " ".join(reviewed.explanation_steps)
    assert "హారం" in " ".join(reviewed.explanation_steps)


def test_reviewer_rejects_reversed_numerator_denominator_positions() -> None:
    lesson = _pure_telugu_fraction_lesson(explanation_steps=[
        "6/8లో లవం 6. లవం భిన్న రేఖకు కింద ఉంటుంది.",
        "6/8లో హారం 8. హారం భిన్న రేఖకు పైన ఉంటుంది.",
    ])
    with pytest.raises(AIReviewerRejectionError) as exc_info:
        LessonReviewer().review(lesson, _fraction_parts_request())
    assert exc_info.value.validation_rule == "malformed_fraction_explanation"


@pytest.mark.parametrize(
    "advanced_text",
    [
        "ఇప్పుడు కనిష్ఠ సామాన్య గుణిజం ఉపయోగించి భిన్నాలను మార్చాలి.",
        "ఇప్పుడు గరిష్ఠ సామాన్య కారణాంకం ఉపయోగించి భిన్నాన్ని కుదించాలి.",
        "తర్వాత అపక్రమ భిన్నం గురించి నేర్చుకోవాలి.",
    ],
)
def test_basic_fraction_question_rejects_unrequested_advanced_scope(advanced_text: str) -> None:
    lesson = _pure_telugu_fraction_lesson(key_points=[advanced_text])
    with pytest.raises(AIReviewerRejectionError) as exc_info:
        LessonReviewer().review(lesson, _fraction_parts_request())
    assert exc_info.value.validation_rule == "excessive_scope"


def test_improper_fraction_is_allowed_when_explicitly_requested() -> None:
    lesson = _pure_telugu_fraction_lesson(
        key_points=["అపక్రమ భిన్నంలో లవం హారం కంటే ఎక్కువగా ఉండవచ్చు."],
    )
    request = _fraction_parts_request("అపక్రమ భిన్నం అంటే ఏమిటి? ఉదాహరణతో వివరించండి.")
    assert LessonReviewer().review(lesson, request).key_points


def test_english_and_telugu_assisted_profiles_are_unaffected_by_script_rule() -> None:
    reviewer = LessonReviewer()
    english = LessonResult(
        **_content().model_dump(),
        source="openai",
        fallback_used=False,
        prompt_id="vedha_mathematics_teacher_v1",
        prompt_version="1.1.0",
    )
    assisted_content = _content(
        title="Fractions ను సులభంగా నేర్చుకుందాం",
        introduction="ఒక whole ను సమాన భాగాలుగా విభజించినప్పుడు ప్రతి భాగాన్ని fraction అంటాము.",
        explanation_steps=["ముందుగా ఒక simple example చూద్దాం."],
        example="ఒక pizza ను నాలుగు సమాన భాగాలుగా చేస్తే ఒక్క భాగం 1/4 అవుతుంది.",
        key_points=["Equal parts ముఖ్యమైనవి."],
        check_question="నాలుగు భాగాలలో ఒక భాగాన్ని ఎలా రాస్తావు?",
        learning_profile="telugu_assisted_english",
    )
    assisted = LessonResult(
        **assisted_content.model_dump(),
        source="openai",
        fallback_used=False,
        prompt_id="vedha_mathematics_teacher_v1",
        prompt_version="1.1.0",
    )
    assert reviewer.review(english, _request()).source == "openai"
    assisted_request = LessonGenerationRequest(
        class_level="5",
        subject="Mathematics",
        learning_profile="telugu_assisted_english",
        student_question="Fraction అంటే ఏమిటి?",
    )
    assert reviewer.review(assisted, assisted_request).source == "openai"


def test_model_schema_rejects_application_owned_metadata() -> None:
    with pytest.raises(Exception):
        GeneratedLessonContent(**_content().model_dump(), source="fallback", fallback_used=True)


class RaisingProvider(LessonProvider):
    def __init__(self, error: Exception) -> None:
        self.error = error

    def generate_lesson(self, request: LessonGenerationRequest) -> LessonResult:
        raise self.error


@pytest.mark.parametrize(
    "error",
    [
        AIConfigurationError("missing key"),
        AIAuthenticationError("bad credential"),
        AIRateLimitError("limited"),
        AITimeoutError("timeout"),
        AIProviderUnavailableError("server failed"),
        AIInvalidResponseError("malformed"),
        AIRefusalError("refused"),
    ],
)
def test_approved_provider_failures_return_complete_fallback(error: Exception) -> None:
    result = LessonGenerationService(_settings(), provider=RaisingProvider(error)).generate_lesson(_request())
    assert result.source == "fallback"
    assert result.fallback_used is True
    assert result.explanation_steps and result.key_points
    assert result.prompt_id and result.prompt_version


def test_missing_api_key_falls_back_without_constructing_a_network_request() -> None:
    service = LessonGenerationService(_settings(openai_api_key=None))
    result = service.generate_lesson(_request())
    assert result.source == "fallback"
    assert service.last_fallback_reason == "missing_configuration"


def test_missing_api_key_fails_safely_when_fallback_disabled() -> None:
    service = LessonGenerationService(_settings(openai_api_key=None, ai_fallback_enabled=False))
    with pytest.raises(AIConfigurationError):
        service.generate_lesson(_request())


def test_reviewer_rejection_uses_fallback() -> None:
    class MismatchedProvider(LessonProvider):
        def generate_lesson(self, request: LessonGenerationRequest) -> LessonResult:
            return LessonResult(
                **_content(subject="Science").model_dump(),
                source="openai",
                fallback_used=False,
                prompt_id="vedha_mathematics_teacher_v1",
                prompt_version="1.0.0",
            )

    service = LessonGenerationService(_settings(), provider=MismatchedProvider())
    result = service.generate_lesson(_request())
    assert result.source == "fallback"
    assert result.subject == "Mathematics"
    assert service.last_fallback_reason == "reviewer_rejection"
    assert service.last_validation_rule == "canonical_metadata_mismatch"


def test_safe_configuration_diagnostic_contains_only_approved_fields() -> None:
    diagnostic = get_safe_ai_configuration(_settings(openai_api_key="never-return-this-key"))
    assert diagnostic == {
        "provider": "openai",
        "model": "configured-test-model",
        "key_configured": True,
        "fallback_enabled": True,
    }
    assert "never-return-this-key" not in str(diagnostic)


@pytest.mark.parametrize(
    ("error", "reason"),
    [
        (AIConfigurationError("safe"), "missing_configuration"),
        (AIAuthenticationError("safe"), "authentication_error"),
        (AIInsufficientQuotaError("safe"), "insufficient_quota"),
        (AIModelNotFoundError("safe"), "model_not_found"),
        (AIRateLimitError("safe"), "rate_limit"),
        (AITimeoutError("safe"), "timeout"),
        (AIInvalidResponseError("safe"), "malformed_response"),
        (AIProviderUnavailableError("safe"), "provider_unavailable"),
    ],
)
def test_service_records_normalized_fallback_reason(error: Exception, reason: str) -> None:
    service = LessonGenerationService(_settings(), provider=RaisingProvider(error))
    result = service.generate_lesson(_request())
    assert result.fallback_used is True
    assert service.last_fallback_reason == reason


def test_empty_and_refusal_responses_are_classified_safely(monkeypatch) -> None:
    responses = [
        SimpleNamespace(output_parsed=None, output=[]),
        SimpleNamespace(
            output_parsed=None,
            output=[SimpleNamespace(content=[SimpleNamespace(type="refusal", refusal="unsafe")])],
        ),
    ]

    class FakeClient:
        def __init__(self, **kwargs):
            self.responses = SimpleNamespace(parse=lambda **call_kwargs: responses.pop(0))

    monkeypatch.setattr("backend.app.ai.providers.openai_provider.OpenAI", FakeClient)
    provider = OpenAIProvider(_settings())
    with pytest.raises(AIInvalidResponseError):
        provider.generate_lesson(_request())
    with pytest.raises(AIRefusalError):
        provider.generate_lesson(_request())


def test_no_fallback_api_error_hides_provider_exception_and_key() -> None:
    secret = "unit-test-secret-key"
    service = LessonGenerationService(
        _settings(openai_api_key=secret, ai_fallback_enabled=False),
        provider=RaisingProvider(AIProviderUnavailableError(f"raw provider failure {secret}")),
    )
    app = create_app(_settings(openai_api_key=secret, ai_fallback_enabled=False))
    app.dependency_overrides[_get_service] = lambda: service

    async def post() -> httpx.Response:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            return await client.post("/api/v1/lessons/explain", json={
                "student_name": "Asha",
                "class_level": 5,
                "subject": "Mathematics",
                "learning_profile": "english_medium",
                "question": "What is a fraction?",
            })

    response = asyncio.run(post())
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "ai_service_unavailable"
    assert secret not in response.text
    assert "raw provider failure" not in response.text
    app.dependency_overrides.clear()


def test_prompt_metadata_is_not_exposed_by_public_api() -> None:
    app = create_app(_settings(openai_api_key=None))

    async def post() -> httpx.Response:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            return await client.post("/api/v1/lessons/explain", json={
                "student_name": "Asha",
                "class_level": 5,
                "subject": "Mathematics",
                "learning_profile": "english_medium",
                "question": "What is a fraction?",
            })

    payload = asyncio.run(post()).json()
    assert "prompt_id" not in payload
    assert "prompt_version" not in payload
    assert "system prompt" not in str(payload).lower()


def test_fallback_reason_is_attached_to_safe_lesson_log(monkeypatch) -> None:
    app = create_app(_settings(openai_api_key=None))
    captured: dict[str, object] = {}
    monkeypatch.setattr(
        "backend.app.api.lessons.logger.info",
        lambda message, *, extra: captured.update({"message": message, **extra}),
    )

    async def post() -> httpx.Response:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            return await client.post("/api/v1/lessons/explain", json={
                "student_name": "Asha",
                "class_level": 5,
                "subject": "Mathematics",
                "learning_profile": "english_medium",
                "question": "What is a fraction?",
            })

    response = asyncio.run(post())
    assert response.status_code == 200
    assert captured["message"] == "Lesson generation completed"
    assert captured["fallback_reason"] == "missing_configuration"
    assert "openai_api_key" not in captured


def test_reviewer_rejects_object_replacement_artifacts_in_assisted_telugu() -> None:
    content = _content(
        title="Geometryను సులభంగా నేర్చుకుందాం",
        introduction="Geometry shapes మరియు angles గురించి వివరిస్తుంది.",
        explanation_steps=["Triangle interior angles మొత్తం 180°. [OBJ][OBJ][OBJ]"],
        example="Triangleలో 50° + 60° ఉంటే third angleను కనుగొనాలి.",
        key_points=["Anglesను జాగ్రత్తగా కలపాలి."],
        check_question="Triangleలో మూడవ angle ఎంత?",
        learning_profile="telugu_assisted_english",
    )
    lesson = LessonResult(
        **content.model_dump(),
        source="openai",
        fallback_used=False,
        prompt_id="vedha_mathematics_teacher_v1",
        prompt_version="1.1.0",
    )
    request = LessonGenerationRequest(
        class_level="5",
        subject="Mathematics",
        learning_profile="telugu_assisted_english",
        student_question="Explain geometry from scratch.",
        concept="Geometry",
    )
    with pytest.raises(AIReviewerRejectionError) as exc_info:
        LessonReviewer().review(lesson, request)
    assert exc_info.value.validation_rule == "encoding_artifact"


def test_prompt_forbids_object_replacement_glyphs() -> None:
    prompt = LessonPromptBuilder().build_request(
        class_level="9",
        subject="Mathematics",
        learning_profile="telugu_assisted_english",
        student_question="Explain geometry from scratch.",
        concept="Geometry",
    )
    assert "Never emit [OBJ]" in prompt.instructions
    assert "plain readable Unicode text only" in prompt.instructions


def test_pure_telugu_geometry_fallback_is_concept_specific() -> None:
    request = LessonGenerationRequest(
        class_level="9",
        subject="Mathematics",
        learning_profile="pure_telugu",
        student_question="జ్యామితిని మొదటి నుండి వివరించండి.",
        concept="Geometry",
    )
    result = DeterministicFallbackLessonGenerator().generate(request)
    content = " ".join([
        result.title, result.introduction, result.example, result.check_question,
        *result.explanation_steps, *result.key_points,
    ])
    assert "జ్యామితి" in content
    assert "త్రిభుజ" in content
    assert "180°" in content
    assert "పునాది భావన" not in result.title


def test_pure_telugu_social_studies_fallback_is_concept_specific() -> None:
    from backend.app.ai.fallback_generator import DeterministicFallbackLessonGenerator
    from backend.app.ai.lesson_models import LessonGenerationRequest

    lesson = DeterministicFallbackLessonGenerator().generate(
        LessonGenerationRequest(
            class_level="9",
            subject="Social Studies",
            learning_profile="pure_telugu",
            student_question="భారత రాజ్యాంగంలోని ప్రాథమిక హక్కులను వివరించండి",
            concept="Indian Constitution",
        )
    )

    assert lesson.source == "fallback"
    assert lesson.fallback_used is True
    assert lesson.title == "భారత రాజ్యాంగం"
    assert "పౌరుల హక్కులు" in lesson.introduction
    assert "సమానత్వ హక్కు" in lesson.example
    assert "foundation" not in " ".join(
        [lesson.title, lesson.introduction, *lesson.explanation_steps, lesson.example]
    ).casefold()


def test_social_studies_prompt_forbids_generic_overview() -> None:
    from backend.app.ai.prompt_builder import LessonPromptBuilder

    prompt = LessonPromptBuilder().build_request(
        class_level="9",
        subject="Social Studies",
        learning_profile="pure_telugu",
        student_question="స్థానిక ప్రభుత్వం గురించి వివరించండి",
        concept="Local Government",
    )

    assert "Social Studies concept rules" in prompt.instructions
    assert "Never answer with generic study advice" in prompt.instructions
    assert "keep every learner-facing sentence in Telugu" in prompt.instructions
