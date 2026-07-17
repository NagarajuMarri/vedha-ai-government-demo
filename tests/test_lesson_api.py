"""Tests for the Sprint 3B controlled lesson API."""

from __future__ import annotations

import asyncio
import json

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
    assert payload["learning_profile"] == "english_medium"
    assert payload["source"] == "openai"
    assert payload["fallback_used"] is False


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
