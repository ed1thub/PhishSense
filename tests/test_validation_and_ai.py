import builtins
import types

import pytest
from pydantic import ValidationError

from app.ai_analysis import generate_ai_explanation
from app.schemas import EmailInput


def test_email_input_rejects_empty_body():
    with pytest.raises(ValidationError):
        EmailInput(body="   ")


def test_email_input_rejects_invalid_url_scheme():
    with pytest.raises(ValidationError):
        EmailInput(body="content", url="ftp://example.com")


def test_generate_ai_explanation_does_not_leak_errors(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key")

    google_module = types.ModuleType("google")

    class FakeModels:
        def generate_content(self, model: str, contents: str):
            raise RuntimeError("sensitive backend details")

    class FakeClient:
        def __init__(self, api_key: str):
            self.models = FakeModels()

    fake_genai = types.SimpleNamespace(Client=FakeClient)
    google_module.genai = fake_genai

    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "google":
            return google_module
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    result = generate_ai_explanation(
        sender="support@example.com",
        subject="Hello",
        body="Body",
        url="https://example.com",
        score=50,
        risk_level="Medium",
        red_flags=["flag"],
    )

    assert "This email scored" in result
    assert "sensitive backend details" not in result
