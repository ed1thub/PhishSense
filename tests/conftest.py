import types

import pytest


@pytest.fixture(autouse=True)
def mock_gemini_client(monkeypatch):
    """Prevent any test from making real Gemini API calls."""
    try:
        from google import genai
    except ImportError:
        return

    class FakeModels:
        def generate_content(self, model: str, contents: str):
            return types.SimpleNamespace(
                text='{"score": 68, "risk_level": "High", "red_flags": ["Urgency language", "Credential request"], "recommended_action": "Do not click links. Verify via official support channels.", "ai_explanation": "This email appears suspicious due to urgency and credential-harvesting language."}'
            )

    class FakeClient:
        def __init__(self, api_key: str):
            self.models = FakeModels()

    monkeypatch.setattr(genai, "Client", FakeClient)


@pytest.fixture(autouse=True)
def reset_rate_limiter_state():
    from app.main import rate_limiter

    rate_limiter.clear()


@pytest.fixture(autouse=True)
def reset_history_store_state():
    from app.main import reset_history_store_for_tests

    reset_history_store_for_tests()
