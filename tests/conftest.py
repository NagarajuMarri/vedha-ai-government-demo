"""Global test isolation from local real-provider credentials."""

import pytest

from backend.app.core.config import get_settings


@pytest.fixture(autouse=True)
def disable_live_openai_for_automated_tests(monkeypatch: pytest.MonkeyPatch):
    """Ensure a developer's ignored backend/.env can never enable test network calls."""

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
