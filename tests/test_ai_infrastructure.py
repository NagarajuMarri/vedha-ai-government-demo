"""Unit tests for the Sprint 3A AI infrastructure scaffold."""

from __future__ import annotations

import pytest

from backend.app.ai.exceptions import (
    AIAuthenticationError,
    AIConfigurationError,
    AIRateLimitError,
    AITimeoutError,
    AIProviderUnavailableError,
    AIInvalidResponseError,
)
from backend.app.ai.language_profiles import get_language_profile, LANGUAGE_PROFILE_IDS
from backend.app.ai.lesson_models import LessonGenerationRequest, LessonResult
from backend.app.ai.prompt_builder import LessonPromptBuilder
from backend.app.ai.fallback_generator import DeterministicFallbackLessonGenerator
from backend.app.ai.providers.openai_provider import OpenAIProvider
from backend.app.core.config import Settings, get_settings


@pytest.fixture(autouse=True)
def clear_settings_cache() -> None:
    get_settings.cache_clear()


def test_settings_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in [
        "VEDHA_PROJECT_NAME",
        "VEDHA_ENVIRONMENT",
        "VEDHA_API_V1_PREFIX",
        "VEDHA_LOG_LEVEL",
        "VEDHA_CORS_ORIGINS",
        "OPENAI_API_KEY",
        "OPENAI_MODEL",
        "OPENAI_TIMEOUT_SECONDS",
        "AI_PROVIDER",
        "AI_FALLBACK_ENABLED",
    ]:
        monkeypatch.delenv(key, raising=False)

    settings = get_settings()

    assert settings.openai_model is None
    assert settings.openai_timeout_seconds is None
    assert settings.ai_provider == "openai"
    assert settings.ai_fallback_enabled is True
    assert settings.openai_api_key is None


def test_missing_openai_key_does_not_crash_startup(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")

    settings = get_settings()

    assert settings.openai_api_key is None
    assert settings.ai_fallback_enabled is True


def test_invalid_timeout_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_TIMEOUT_SECONDS", "not-a-number")

    with pytest.raises(ValueError):
        get_settings()


def test_language_profiles_are_exactly_three_approved_ids() -> None:
    assert LANGUAGE_PROFILE_IDS == {
        "english_medium",
        "telugu_assisted_english",
        "pure_telugu",
    }


def test_english_medium_profile_rules() -> None:
    profile = get_language_profile("english_medium")
    assert profile.explanation_language == "English"
    assert profile.terminology_language == "English"
    assert "English" in profile.concise_prompt_instructions


def test_telugu_profile_rules() -> None:
    telugu_assisted = get_language_profile("telugu_assisted_english")
    pure_telugu = get_language_profile("pure_telugu")

    assert "Telugu" in telugu_assisted.explanation_language
    assert "English" not in telugu_assisted.concise_prompt_instructions or "fully English" in telugu_assisted.forbidden_behaviour
    assert "తెలుగు" in pure_telugu.concise_prompt_instructions
    assert "fully English" in pure_telugu.forbidden_behaviour
    assert "Unavoidable English terms may appear in parentheses only when useful" in pure_telugu.concise_prompt_instructions


def test_prompt_builder_includes_required_evidence() -> None:
    prompt = LessonPromptBuilder().build(
        class_level="5",
        subject="Mathematics",
        learning_profile="telugu_assisted_english",
        student_question="What is a fraction?",
    )

    assert "Class 5" in prompt
    assert "Mathematics" in prompt
    assert "telugu_assisted_english" in prompt
    assert "step-by-step" in prompt.lower()
    assert "simple example" in prompt.lower()
    assert "structured output" in prompt.lower()
    assert "15-question practice" not in prompt.lower()
    assert "answer evaluation" not in prompt.lower()


def test_fallback_is_deterministic_for_identical_inputs() -> None:
    request = LessonGenerationRequest(
        class_level="7",
        subject="Science",
        learning_profile="pure_telugu",
        student_question="Explain gravity.",
    )
    generator = DeterministicFallbackLessonGenerator()

    first = generator.generate(request)
    second = generator.generate(request)

    assert first == second
    assert first.source == "fallback"
    assert first.fallback_used is True


def test_fallback_respects_all_profiles() -> None:
    generator = DeterministicFallbackLessonGenerator()

    for profile in ("english_medium", "telugu_assisted_english", "pure_telugu"):
        result = generator.generate(
            LessonGenerationRequest(
                class_level="4",
                subject="English",
                learning_profile=profile,
                student_question="What is a noun?",
            )
        )
        assert result.learning_profile == profile
        assert result.source == "fallback"
        assert result.fallback_used is True


def test_provider_missing_key_prevents_network_call(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    provider = OpenAIProvider(Settings(
        project_name="Vedha AI Government Demo",
        environment="development",
        api_v1_prefix="/api/v1",
        log_level="INFO",
        cors_origins=("http://localhost:8080",),
        openai_api_key=None,
        openai_model="gpt-4o-mini",
        openai_timeout_seconds=20,
        ai_provider="openai",
        ai_fallback_enabled=True,
    ))

    with pytest.raises(AIConfigurationError):
        provider.generate_lesson(LessonGenerationRequest(
            class_level="6",
            subject="History",
            learning_profile="english_medium",
            student_question="Who was Ashoka?",
        ))


def test_openai_provider_successfully_returns_structured_lesson(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeResponses:
        def parse(self, **kwargs):
            payload = kwargs["text_format"](
                title="Fractions basics",
                introduction="A fraction shows part of a whole.",
                explanation_steps=["A fraction has a numerator and denominator."],
                example="Half is shown by the fraction 1/2.",
                key_points=["Numerator shows part", "Denominator shows whole"],
                check_question="Can you identify the numerator in 3/4?",
                learning_profile="english_medium",
                subject="Mathematics",
                class_level="5",
            )
            return type(
                "Result",
                (),
                {"output_parsed": payload, "output": []},
            )()

    class FakeClient:
        def __init__(self, *args, **kwargs):
            self.responses = FakeResponses()

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr("backend.app.ai.providers.openai_provider.OpenAI", FakeClient)

    provider = OpenAIProvider(Settings(
        project_name="Vedha AI Government Demo",
        environment="development",
        api_v1_prefix="/api/v1",
        log_level="INFO",
        cors_origins=("http://localhost:8080",),
        openai_api_key="test-key",
        openai_model="gpt-4o-mini",
        openai_timeout_seconds=20,
        ai_provider="openai",
        ai_fallback_enabled=True,
    ))

    result = provider.generate_lesson(LessonGenerationRequest(
        class_level="5",
        subject="Mathematics",
        learning_profile="english_medium",
        student_question="What is a fraction?",
    ))

    assert isinstance(result, LessonResult)
    assert result.source == "openai"
    assert result.fallback_used is False


def test_provider_maps_timeout_to_internal_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class TimeoutError(Exception):
        pass

    class FakeClient:
        def __init__(self, *args, **kwargs):
            self.responses = type("Responses", (), {"parse": lambda self, **kwargs: (_ for _ in ()).throw(TimeoutError("timeout"))})()

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr("backend.app.ai.providers.openai_provider.OpenAI", FakeClient)

    provider = OpenAIProvider(Settings(
        project_name="Vedha AI Government Demo",
        environment="development",
        api_v1_prefix="/api/v1",
        log_level="INFO",
        cors_origins=("http://localhost:8080",),
        openai_api_key="test-key",
        openai_model="gpt-4o-mini",
        openai_timeout_seconds=20,
        ai_provider="openai",
        ai_fallback_enabled=True,
    ))

    with pytest.raises(AITimeoutError):
        provider.generate_lesson(LessonGenerationRequest(
            class_level="6",
            subject="Science",
            learning_profile="english_medium",
            student_question="What is energy?",
        ))


def test_provider_maps_rate_limit_to_internal_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class RateLimitError(Exception):
        pass

    class FakeClient:
        def __init__(self, *args, **kwargs):
            self.responses = type("Responses", (), {"parse": lambda self, **kwargs: (_ for _ in ()).throw(RateLimitError("too many requests"))})()

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr("backend.app.ai.providers.openai_provider.OpenAI", FakeClient)

    provider = OpenAIProvider(Settings(
        project_name="Vedha AI Government Demo",
        environment="development",
        api_v1_prefix="/api/v1",
        log_level="INFO",
        cors_origins=("http://localhost:8080",),
        openai_api_key="test-key",
        openai_model="gpt-4o-mini",
        openai_timeout_seconds=20,
        ai_provider="openai",
        ai_fallback_enabled=True,
    ))

    with pytest.raises(AIRateLimitError):
        provider.generate_lesson(LessonGenerationRequest(
            class_level="6",
            subject="Science",
            learning_profile="english_medium",
            student_question="What is energy?",
        ))


def test_provider_maps_authentication_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    class AuthenticationError(Exception):
        pass

    class FakeClient:
        def __init__(self, *args, **kwargs):
            self.responses = type("Responses", (), {"parse": lambda self, **kwargs: (_ for _ in ()).throw(AuthenticationError("bad key"))})()

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr("backend.app.ai.providers.openai_provider.OpenAI", FakeClient)

    provider = OpenAIProvider(Settings(
        project_name="Vedha AI Government Demo",
        environment="development",
        api_v1_prefix="/api/v1",
        log_level="INFO",
        cors_origins=("http://localhost:8080",),
        openai_api_key="test-key",
        openai_model="gpt-4o-mini",
        openai_timeout_seconds=20,
        ai_provider="openai",
        ai_fallback_enabled=True,
    ))

    with pytest.raises(AIAuthenticationError):
        provider.generate_lesson(LessonGenerationRequest(
            class_level="6",
            subject="Science",
            learning_profile="english_medium",
            student_question="What is energy?",
        ))


def test_provider_maps_unavailable_provider_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class UnavailableError(Exception):
        pass

    class FakeClient:
        def __init__(self, *args, **kwargs):
            self.responses = type("Responses", (), {"parse": lambda self, **kwargs: (_ for _ in ()).throw(UnavailableError("unavailable"))})()

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr("backend.app.ai.providers.openai_provider.OpenAI", FakeClient)

    provider = OpenAIProvider(Settings(
        project_name="Vedha AI Government Demo",
        environment="development",
        api_v1_prefix="/api/v1",
        log_level="INFO",
        cors_origins=("http://localhost:8080",),
        openai_api_key="test-key",
        openai_model="gpt-4o-mini",
        openai_timeout_seconds=20,
        ai_provider="openai",
        ai_fallback_enabled=True,
    ))

    with pytest.raises(AIProviderUnavailableError):
        provider.generate_lesson(LessonGenerationRequest(
            class_level="6",
            subject="Science",
            learning_profile="english_medium",
            student_question="What is energy?",
        ))


def test_provider_invalid_response_mapping(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeResponses:
        def parse(self, **kwargs):
            return type(
                "Result",
                (),
                {
                    "output_parsed": {
                        "title": "Fractions basics",
                        "introduction": "A fraction shows part of a whole.",
                        "explanation_steps": [],
                        "example": "Half is shown by 1/2.",
                        "key_points": ["Numerator shows part"],
                        "check_question": "Can you identify the numerator in 3/4?",
                        "learning_profile": "english_medium",
                        "subject": "Mathematics",
                        "class_level": "5",
                    },
                    "output": [],
                },
            )()

    class FakeClient:
        def __init__(self, *args, **kwargs):
            self.responses = FakeResponses()

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr("backend.app.ai.providers.openai_provider.OpenAI", FakeClient)

    provider = OpenAIProvider(Settings(
        project_name="Vedha AI Government Demo",
        environment="development",
        api_v1_prefix="/api/v1",
        log_level="INFO",
        cors_origins=("http://localhost:8080",),
        openai_api_key="test-key",
        openai_model="gpt-4o-mini",
        openai_timeout_seconds=20,
        ai_provider="openai",
        ai_fallback_enabled=True,
    ))

    with pytest.raises(AIInvalidResponseError):
        provider.generate_lesson(LessonGenerationRequest(
            class_level="5",
            subject="Mathematics",
            learning_profile="english_medium",
            student_question="What is a fraction?",
        ))
