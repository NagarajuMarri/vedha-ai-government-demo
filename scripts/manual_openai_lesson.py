"""Explicit, one-request manual OpenAI integration check that consumes API credits."""

from __future__ import annotations

import argparse
import os

from backend.app.ai.lesson_models import LessonGenerationRequest
from backend.app.ai.providers.openai_provider import OpenAIProvider
from backend.app.core.config import get_settings


def main() -> None:
    parser = argparse.ArgumentParser(description="Send one controlled lesson request to OpenAI.")
    parser.add_argument(
        "--i-understand-this-uses-api-credits",
        action="store_true",
        help="Required acknowledgement that this command makes a billable API request.",
    )
    args = parser.parse_args()
    if not args.i_understand_this_uses_api_credits:
        parser.error("This uses API credits; pass --i-understand-this-uses-api-credits to continue.")
    if not os.getenv("OPENAI_API_KEY", "").strip():
        parser.error("OPENAI_API_KEY must be set in the backend environment.")

    print("WARNING: sending one real OpenAI request that may use API credits.")
    result = OpenAIProvider(get_settings()).generate_lesson(LessonGenerationRequest(
        class_level="5",
        subject="Mathematics",
        learning_profile="english_medium",
        student_question="What is a fraction?",
    ))
    print({
        "title": result.title,
        "subject": result.subject,
        "class_level": result.class_level,
        "learning_profile": result.learning_profile,
        "source": result.source,
        "prompt_id": result.prompt_id,
        "prompt_version": result.prompt_version,
    })


if __name__ == "__main__":
    main()
