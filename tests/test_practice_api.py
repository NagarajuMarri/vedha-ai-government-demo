"""Sprint 4D exact-composition practice API tests."""

from __future__ import annotations

import asyncio
from collections import Counter

import httpx
import pytest
from pydantic import ValidationError

from backend.app.main import app
from backend.app.practice.models import PracticeQuestion, PracticeSet


def _post(payload: dict[str, object]) -> httpx.Response:
    async def request() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.post("/api/v1/practice/generate", json=payload)
    return asyncio.run(request())


def _payload(profile: str = "english_medium") -> dict[str, object]:
    return {
        "student_name": "Asha",
        "class_level": 5,
        "subject": "Mathematics",
        "concept": "Fractions",
        "learning_profile": profile,
    }


def test_generate_returns_exactly_five_questions_per_difficulty() -> None:
    response = _post(_payload())
    assert response.status_code == 200
    body = response.json()
    assert len(body["questions"]) == 15
    assert Counter(question["difficulty"] for question in body["questions"]) == {
        "easy": 5,
        "medium": 5,
        "hard": 5,
    }
    assert len({question["question_id"] for question in body["questions"]}) == 15
    assert len({question["prompt"] for question in body["questions"]}) == 15


def test_all_learning_profiles_have_complete_questions() -> None:
    for profile in ("english_medium", "telugu_assisted_english", "pure_telugu"):
        body = _post(_payload(profile)).json()
        assert body["learning_profile"] == profile
        assert all(question["prompt"].strip() and question["hint"].strip() for question in body["questions"])
        if profile == "pure_telugu":
            assert all(any("\u0c00" <= char <= "\u0c7f" for char in question["prompt"]) for question in body["questions"])


def test_invalid_request_is_rejected() -> None:
    payload = _payload()
    payload["class_level"] = 13
    response = _post(payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_domain_rejects_wrong_difficulty_composition() -> None:
    questions = [
        PracticeQuestion(question_id=f"q-{index}", difficulty="easy", prompt=f"Explain practice item number {index}.", hint="Use the key rule.")
        for index in range(15)
    ]
    with pytest.raises(ValidationError, match="exactly 5 easy"):
        PracticeSet(
            practice_set_id="practice-test",
            class_level=5,
            subject="Mathematics",
            concept="Fractions",
            learning_profile="english_medium",
            questions=questions,
        )


def test_openapi_lists_practice_endpoint() -> None:
    assert "/api/v1/practice/generate" in app.openapi()["paths"]
