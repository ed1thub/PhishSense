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
            return types.SimpleNamespace(text="Mocked AI explanation")

    class FakeClient:
        def __init__(self, api_key: str):
            self.models = FakeModels()

    monkeypatch.setattr(genai, "Client", FakeClient)
