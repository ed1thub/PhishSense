from app.settings import get_settings


def test_settings_defaults(monkeypatch):
    monkeypatch.delenv("PHISHSENSE_APP_NAME", raising=False)
    monkeypatch.delenv("PHISHSENSE_LOG_LEVEL", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("PHISHSENSE_GEMINI_MODEL", raising=False)
    monkeypatch.delenv("PHISHSENSE_RULES_FILE", raising=False)

    settings = get_settings()

    assert settings.app_name == "PhishSense"
    assert settings.log_level == "INFO"
    assert settings.gemini_model == "gemini-2.5-flash"
    assert settings.gemini_api_key == ""
    assert settings.rules_file == ""


def test_settings_from_environment(monkeypatch):
    monkeypatch.setenv("PHISHSENSE_APP_NAME", "PhishSense Test")
    monkeypatch.setenv("PHISHSENSE_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("GEMINI_API_KEY", "abc123")
    monkeypatch.setenv("PHISHSENSE_GEMINI_MODEL", "gemini-test")
    monkeypatch.setenv("PHISHSENSE_RULES_FILE", "/tmp/rules.yaml")

    settings = get_settings()

    assert settings.app_name == "PhishSense Test"
    assert settings.log_level == "DEBUG"
    assert settings.gemini_api_key == "abc123"
    assert settings.gemini_model == "gemini-test"
    assert settings.rules_file == "/tmp/rules.yaml"
