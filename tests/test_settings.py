from app.settings import get_settings


def test_settings_defaults(monkeypatch):
    monkeypatch.delenv("PHISHSENSE_APP_NAME", raising=False)
    monkeypatch.delenv("PHISHSENSE_LOG_LEVEL", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("PHISHSENSE_GEMINI_MODEL", raising=False)
    monkeypatch.delenv("PHISHSENSE_RULES_FILE", raising=False)
    monkeypatch.delenv("PHISHSENSE_RATE_LIMIT_ENABLED", raising=False)
    monkeypatch.delenv("PHISHSENSE_RATE_LIMIT_REQUESTS", raising=False)
    monkeypatch.delenv("PHISHSENSE_RATE_LIMIT_WINDOW_SECONDS", raising=False)
    monkeypatch.delenv("PHISHSENSE_ADMIN_MODE_ENABLED", raising=False)
    monkeypatch.delenv("PHISHSENSE_ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("PHISHSENSE_ADMIN_PASSWORD", raising=False)
    monkeypatch.delenv("PHISHSENSE_HISTORY_ENABLED", raising=False)
    monkeypatch.delenv("PHISHSENSE_HISTORY_DB_PATH", raising=False)
    monkeypatch.delenv("PHISHSENSE_HISTORY_MAX_RESULTS", raising=False)

    settings = get_settings()

    assert settings.app_name == "PhishSense"
    assert settings.log_level == "INFO"
    assert settings.gemini_model == "gemini-2.5-flash"
    assert settings.gemini_api_key == ""
    assert settings.rules_file == ""
    assert settings.rate_limit_enabled is True
    assert settings.rate_limit_requests == 60
    assert settings.rate_limit_window_seconds == 60
    assert settings.admin_mode_enabled is False
    assert settings.admin_username == ""
    assert settings.admin_password == ""
    assert settings.history_enabled is True
    assert settings.history_db_path == "phishsense_history.db"
    assert settings.history_max_results == 100


def test_settings_from_environment(monkeypatch):
    monkeypatch.setenv("PHISHSENSE_APP_NAME", "PhishSense Test")
    monkeypatch.setenv("PHISHSENSE_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("GEMINI_API_KEY", "abc123")
    monkeypatch.setenv("PHISHSENSE_GEMINI_MODEL", "gemini-test")
    monkeypatch.setenv("PHISHSENSE_RULES_FILE", "/tmp/rules.yaml")
    monkeypatch.setenv("PHISHSENSE_RATE_LIMIT_ENABLED", "false")
    monkeypatch.setenv("PHISHSENSE_RATE_LIMIT_REQUESTS", "15")
    monkeypatch.setenv("PHISHSENSE_RATE_LIMIT_WINDOW_SECONDS", "30")
    monkeypatch.setenv("PHISHSENSE_ADMIN_MODE_ENABLED", "true")
    monkeypatch.setenv("PHISHSENSE_ADMIN_USERNAME", "admin")
    monkeypatch.setenv("PHISHSENSE_ADMIN_PASSWORD", "secret")
    monkeypatch.setenv("PHISHSENSE_HISTORY_ENABLED", "false")
    monkeypatch.setenv("PHISHSENSE_HISTORY_DB_PATH", "/tmp/history.db")
    monkeypatch.setenv("PHISHSENSE_HISTORY_MAX_RESULTS", "40")

    settings = get_settings()

    assert settings.app_name == "PhishSense Test"
    assert settings.log_level == "DEBUG"
    assert settings.gemini_api_key == "abc123"
    assert settings.gemini_model == "gemini-test"
    assert settings.rules_file == "/tmp/rules.yaml"
    assert settings.rate_limit_enabled is False
    assert settings.rate_limit_requests == 15
    assert settings.rate_limit_window_seconds == 30
    assert settings.admin_mode_enabled is True
    assert settings.admin_username == "admin"
    assert settings.admin_password == "secret"
    assert settings.history_enabled is False
    assert settings.history_db_path == "/tmp/history.db"
    assert settings.history_max_results == 40
