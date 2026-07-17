from openai import OpenAI

from backend.app.ai.lesson_models import GeneratedLessonContent
from backend.app.core.config import get_settings


def main() -> None:
    settings = get_settings()

    print("Model:", settings.openai_model)
    print("Key loaded:", bool(settings.openai_api_key))

    client = OpenAI(
        api_key=settings.openai_api_key,
        timeout=60,
    )

    response = client.responses.parse(
        model=settings.openai_model,
        instructions=(
            "You are a Class 5 mathematics teacher. "
            "Explain fractions in simple Telugu. "
            "Return the requested structured lesson."
        ),
        input="భిన్నాలు, లవం మరియు హారం ఉదాహరణతో వివరించండి.",
        text_format=GeneratedLessonContent,
        store=False,
    )

    parsed = response.output_parsed

    print("Parsed:", parsed is not None)

    if parsed is not None:
        print(parsed.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
