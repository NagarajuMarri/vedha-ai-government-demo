"""Tests for the Sprint 3B controlled lesson API."""

from __future__ import annotations

import asyncio
import re

import httpx

from backend.app.ai.lesson_models import LessonGenerationRequest, LessonResult
from backend.app.main import app


def _post(payload: dict[str, object]) -> httpx.Response:
    async def request() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.post("/api/v1/lessons/explain", json=payload)

    return asyncio.run(request())


def test_valid_english_medium_request_success(monkeypatch) -> None:
    async def fake_generate(self, request: LessonGenerationRequest) -> LessonResult:
        return LessonResult(
            title="Fractions basics",
            introduction="A fraction shows part of a whole.",
            explanation_steps=["A numerator tells how many parts you have.", "A denominator tells how many equal parts make the whole."],
            example="If you divide a pizza into 4 equal pieces and take 1 piece, that is 1/4.",
            key_points=["The numerator is the top number.", "The denominator is the bottom number."],
            check_question="What does the denominator tell you in 3/4?",
            learning_profile="english_medium",
            subject="Mathematics",
            class_level="5",
            source="openai",
            fallback_used=False,
            prompt_id="vedha_mathematics_teacher_v1",
            prompt_version="1.0.0",
        )

    monkeypatch.setattr(
        "backend.app.api.lessons.LessonGenerationService.generate_lesson",
        fake_generate,
    )

    response = _post(
        {
            "student_name": "Asha",
            "class_level": 5,
            "subject": "Mathematics",
            "learning_profile": "english_medium",
            "question": "What is a fraction?",
        }
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["request_id"]
    assert payload["lesson_id"]
    assert payload["title"] == "Fractions basics"
    assert payload["introduction"]
    assert payload["explanation_steps"]
    assert payload["example"]
    assert payload["key_points"]
    assert payload["check_question"]
    assert payload["created_at"]
    assert payload["learning_profile"] == "english_medium"
    assert payload["source"] == "openai"
    assert payload["fallback_used"] is False


def test_fallback_responses_include_complete_content_for_all_profiles() -> None:
    required_text_fields = (
        "title",
        "introduction",
        "example",
        "check_question",
    )

    for profile in ("english_medium", "telugu_assisted_english", "pure_telugu"):
        response = _post(
            {
                "student_name": "Asha",
                "class_level": 5,
                "subject": "Mathematics",
                "learning_profile": profile,
                "question": "What is a fraction?",
            }
        )

        assert response.status_code == 200
        payload = response.json()
        assert all(payload[field].strip() for field in required_text_fields)
        assert isinstance(payload["explanation_steps"], list)
        assert payload["explanation_steps"]
        assert all(step.strip() for step in payload["explanation_steps"])
        assert isinstance(payload["key_points"], list)
        assert payload["key_points"]
        assert all(point.strip() for point in payload["key_points"])
        assert payload["created_at"]
        assert payload["source"] == "fallback"
        assert payload["fallback_used"] is True

        if profile == "pure_telugu":
            telugu_pattern = r"[\u0C00-\u0C7F]"
            assert all(
                re.search(telugu_pattern, payload[field])
                for field in required_text_fields
            )
            assert all(
                re.search(telugu_pattern, step)
                for step in payload["explanation_steps"]
            )
            assert all(
                re.search(telugu_pattern, point)
                for point in payload["key_points"]
            )


def test_invalid_class_below_one_returns_validation_error() -> None:
    response = _post(
        {
            "student_name": "Asha",
            "class_level": 0,
            "subject": "Mathematics",
            "learning_profile": "english_medium",
            "question": "What is a fraction?",
        }
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "validation_error"


def test_question_over_1500_characters_returns_validation_error() -> None:
    response = _post(
        {
            "student_name": "Asha",
            "class_level": 5,
            "subject": "Mathematics",
            "learning_profile": "english_medium",
            "question": "x" * 1501,
        }
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_openapi_lists_lesson_endpoint() -> None:
    response = _post({
        "student_name": "Asha",
        "class_level": 5,
        "subject": "Mathematics",
        "learning_profile": "english_medium",
        "question": "What is a fraction?",
    })

    assert response.status_code == 200
    openapi = app.openapi()
    assert "/api/v1/lessons/explain" in openapi["paths"]


def test_lesson_request_carries_selected_concept_into_generation() -> None:
    payload = {
        "student_name": "Asha",
        "class_level": 9,
        "subject": "Mathematics",
        "concept": "Fractions",
        "learning_profile": "pure_telugu",
        "question": "Explain fractions from scratch.",
    }
    request = ExplainLessonRequest.model_validate(payload)
    generation = LessonGenerationRequest(
        class_level=str(request.class_level),
        subject=request.subject,
        learning_profile=request.learning_profile,
        student_question=request.question,
        concept=request.concept,
    )
    prompt = LessonPromptBuilder().build_request(
        class_level=generation.class_level,
        subject=generation.subject,
        learning_profile=generation.learning_profile,
        student_question=generation.student_question,
        concept=generation.concept,
    )
    assert "required lesson concept is: Fractions" in prompt.instructions
    assert "Do not replace the requested concept with a broad subject overview" in prompt.instructions
    assert "Selected concept (trusted application context): Fractions" in prompt.student_input
