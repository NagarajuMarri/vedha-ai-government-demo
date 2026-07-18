"""Sprint 4D exact-composition practice API tests."""

from __future__ import annotations

import asyncio
import base64
from collections import Counter
from dataclasses import replace
from types import SimpleNamespace

import httpx
import pytest
from pydantic import ValidationError

from backend.app.core.config import get_settings
from backend.app.main import app
from backend.app.practice.handwriting import (
    HandwritingEvaluationService,
    HandwritingImageError,
    HandwritingVisionResult,
)
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


def _evaluate(payload: dict[str, object]) -> httpx.Response:
    async def request() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.post("/api/v1/practice/evaluate", json=payload)
    return asyncio.run(request())


def test_correct_typed_answer_receives_positive_feedback() -> None:
    practice = _post(_payload()).json()
    question = practice["questions"][0]
    response = _evaluate({
        "practice_set_id": practice["practice_set_id"],
        "question_id": question["question_id"],
        "student_answer": "1/2",
    })
    assert response.status_code == 200
    body = response.json()
    assert body["correct"] is True
    assert body["feedback"]
    assert body["corrective_guidance"]


def test_wrong_answer_teaches_without_only_revealing_final_answer() -> None:
    practice = _post(_payload("pure_telugu")).json()
    question = practice["questions"][0]
    response = _evaluate({
        "practice_set_id": practice["practice_set_id"],
        "question_id": question["question_id"],
        "student_answer": "3/4",
    })
    assert response.status_code == 200
    body = response.json()
    assert body["correct"] is False
    assert len(body["corrective_guidance"]) >= 2
    assert "1/2" not in body["feedback"]
    assert all("1/2" not in step for step in body["corrective_guidance"])
    assert any("\u0c00" <= char <= "\u0c7f" for char in body["feedback"])


def test_unknown_question_cannot_be_evaluated() -> None:
    response = _evaluate({
        "practice_set_id": "practice-missing",
        "question_id": "question-missing",
        "student_answer": "answer",
    })
    assert response.status_code == 404


def test_openapi_lists_practice_evaluation_endpoint() -> None:
    assert "/api/v1/practice/evaluate" in app.openapi()["paths"]


def test_fraction_wrong_answer_returns_calculation_specific_guidance() -> None:
    practice = _post(_payload()).json()
    question = practice["questions"][5]
    response = _evaluate({
        "practice_set_id": practice["practice_set_id"],
        "question_id": question["question_id"],
        "student_answer": "3/4",
    })
    body = response.json()
    guidance = " ".join(body["corrective_guidance"])
    assert body["correct"] is False
    assert "greatest common divisor" in guidance
    assert "Cross-check equivalence" in guidance
    assert "3 × 12" in guidance
    assert body["attempt_number"] == 1


def test_practice_attempt_number_increments_for_same_question() -> None:
    practice = _post(_payload()).json()
    question = practice["questions"][1]
    payload = {
        "practice_set_id": practice["practice_set_id"],
        "question_id": question["question_id"],
        "student_answer": "3/4",
    }
    first = _evaluate(payload).json()
    second = _evaluate(payload).json()
    assert first["attempt_number"] == 1
    assert second["attempt_number"] == 2
    assert "Attempt 2" in second["feedback"]


def test_handwriting_evaluation_uses_vision_without_persisting_image() -> None:
    practice = _post(_payload()).json()
    question = practice["questions"][0]
    parsed = HandwritingVisionResult(
        transcribed_work="1/2",
        correct=True,
        feedback="The handwritten simplification is correct.",
        corrective_guidance=["The numerator and denominator were simplified consistently."],
        confidence=0.96,
    )

    class FakeResponses:
        def __init__(self) -> None:
            self.call: dict[str, object] = {}

        def parse(self, **kwargs):
            self.call = kwargs
            return SimpleNamespace(output_parsed=parsed)

    responses = FakeResponses()
    client = SimpleNamespace(responses=responses)
    service = HandwritingEvaluationService(
        settings=replace(get_settings(), openai_api_key="test-key", openai_model="test-vision"),
        client=client,
    )
    image = "data:image/png;base64," + base64.b64encode(b"small-phone-photo").decode()
    result = service.evaluate(
        practice_set_id=practice["practice_set_id"],
        question_id=question["question_id"],
        image_data_url=image,
    )
    assert result["correct"] is True
    assert result["transcribed_work"] == "1/2"
    assert result["confidence"] == 0.96
    assert responses.call["store"] is False
    assert responses.call["input"][0]["content"][1]["type"] == "input_image"


def test_handwriting_rejects_non_image_data() -> None:
    practice = _post(_payload()).json()
    question = practice["questions"][0]
    service = HandwritingEvaluationService(settings=get_settings())
    with pytest.raises(HandwritingImageError):
        service.evaluate(
            practice_set_id=practice["practice_set_id"],
            question_id=question["question_id"],
            image_data_url="data:text/plain;base64,SGVsbG8=",
        )


def test_openapi_lists_handwriting_endpoint() -> None:
    assert "/api/v1/practice/evaluate-handwriting" in app.openapi()["paths"]
