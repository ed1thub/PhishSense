from fastapi.testclient import TestClient

from app.main import app


def test_home_page_renders_html():
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "PhishSense" in response.text


def test_analyze_endpoint_returns_expected_shape_for_valid_payload(monkeypatch):
    client = TestClient(app)

    monkeypatch.setattr(
        "app.main.generate_ai_assessment",
        lambda **kwargs: {
            "score": 76,
            "risk_level": "High",
            "red_flags": ["Credential request detected", "Urgency pressure"],
            "recommended_action": "Avoid the link and verify through official support.",
            "ai_explanation": "This message appears high risk due to urgency and credential prompts.",
            "source": "ai",
        },
    )

    payload = {
        "sender": "support@micros0ft-login.com",
        "subject": "Urgent: Verify your account now",
        "body": "Your account will be suspended immediately. Log in and confirm your password now!",
        "url": "https://bit.ly/fake-login",
    }

    response = client.post("/analyze", json=payload)
    data = response.json()

    assert response.status_code == 200
    assert set(data.keys()) == {
        "score",
        "risk_level",
        "red_flags",
        "rule_hits",
        "ai_explanation",
        "recommended_action",
    }
    assert data["risk_level"] in {"Low", "Medium", "High"}
    assert isinstance(data["score"], int)
    assert isinstance(data["red_flags"], list)
    assert isinstance(data["rule_hits"], list)
    assert data["ai_explanation"] == "This message appears high risk due to urgency and credential prompts."


def test_analyze_endpoint_rejects_invalid_url_scheme():
    client = TestClient(app)

    response = client.post(
        "/analyze",
        json={
            "sender": "support@example.com",
            "subject": "Hello",
            "body": "Message body",
            "url": "ftp://example.com",
        },
    )

    assert response.status_code == 422
    detail = response.json().get("detail", [])
    assert any(item.get("loc") == ["body", "url"] for item in detail)


def test_analyze_endpoint_rejects_empty_body():
    client = TestClient(app)

    response = client.post(
        "/analyze",
        json={
            "sender": "support@example.com",
            "subject": "Hello",
            "body": "   ",
            "url": "https://example.com",
        },
    )

    assert response.status_code == 422
    detail = response.json().get("detail", [])
    assert any(item.get("loc") == ["body", "body"] for item in detail)


def test_analyze_endpoint_handles_ai_failures_safely(monkeypatch):
    client = TestClient(app)

    def raise_ai_error(**kwargs):
        raise RuntimeError("simulated ai failure")

    monkeypatch.setattr("app.main.generate_ai_assessment", raise_ai_error)

    response = client.post(
        "/analyze",
        json={
            "sender": "support@example.com",
            "subject": "Status update",
            "body": "Please review the attached project update.",
            "url": "https://example.com/update",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "This email scored" in data["ai_explanation"]


def test_analyze_endpoint_rate_limits_by_client(monkeypatch):
    client = TestClient(app)

    monkeypatch.setenv("PHISHSENSE_RATE_LIMIT_ENABLED", "true")
    monkeypatch.setenv("PHISHSENSE_RATE_LIMIT_REQUESTS", "2")
    monkeypatch.setenv("PHISHSENSE_RATE_LIMIT_WINDOW_SECONDS", "60")
    monkeypatch.setattr(
        "app.main.generate_ai_assessment",
        lambda **kwargs: {
            "score": 42,
            "risk_level": "Medium",
            "red_flags": ["Suspicious tone"],
            "recommended_action": "Verify authenticity through official channels.",
            "ai_explanation": "Potential phishing indicators were detected.",
            "source": "ai",
        },
    )

    payload = {
        "sender": "support@example.com",
        "subject": "Status update",
        "body": "Please review the attached project update.",
        "url": "https://example.com/update",
    }

    response_1 = client.post("/analyze", json=payload)
    response_2 = client.post("/analyze", json=payload)
    response_3 = client.post("/analyze", json=payload)

    assert response_1.status_code == 200
    assert response_2.status_code == 200
    assert response_3.status_code == 429
    assert response_3.headers.get("Retry-After") is not None

    body = response_3.json()
    assert body["detail"] == "Too many requests. Please try again later."
    assert body["retry_after_seconds"] >= 1


def test_admin_endpoint_hidden_when_disabled(monkeypatch):
    client = TestClient(app)

    monkeypatch.setenv("PHISHSENSE_ADMIN_MODE_ENABLED", "false")

    response = client.get("/admin")

    assert response.status_code == 404


def test_admin_endpoint_requires_valid_basic_auth(monkeypatch):
    client = TestClient(app)

    monkeypatch.setenv("PHISHSENSE_ADMIN_MODE_ENABLED", "true")
    monkeypatch.setenv("PHISHSENSE_ADMIN_USERNAME", "admin")
    monkeypatch.setenv("PHISHSENSE_ADMIN_PASSWORD", "secret")

    response = client.get("/admin")

    assert response.status_code == 401
    assert response.headers.get("WWW-Authenticate") == "Basic"


def test_admin_endpoint_returns_503_if_credentials_missing(monkeypatch):
    client = TestClient(app)

    monkeypatch.setenv("PHISHSENSE_ADMIN_MODE_ENABLED", "true")
    monkeypatch.delenv("PHISHSENSE_ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("PHISHSENSE_ADMIN_PASSWORD", raising=False)

    response = client.get("/admin", auth=("any", "thing"))

    assert response.status_code == 503
    assert response.json()["detail"] == "Admin credentials are not configured."


def test_admin_endpoint_allows_authorized_user(monkeypatch):
    client = TestClient(app)

    monkeypatch.setenv("PHISHSENSE_ADMIN_MODE_ENABLED", "true")
    monkeypatch.setenv("PHISHSENSE_ADMIN_USERNAME", "admin")
    monkeypatch.setenv("PHISHSENSE_ADMIN_PASSWORD", "secret")
    monkeypatch.setenv("PHISHSENSE_RATE_LIMIT_REQUESTS", "11")
    monkeypatch.setenv("PHISHSENSE_RATE_LIMIT_WINDOW_SECONDS", "45")

    response = client.get("/admin", auth=("admin", "secret"))

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Admin mode enabled"
    assert body["admin_user"] == "admin"
    assert body["rate_limit"]["requests"] == 11
    assert body["rate_limit"]["window_seconds"] == 45


def test_admin_history_returns_saved_analysis(monkeypatch, tmp_path):
    client = TestClient(app)

    monkeypatch.setenv("PHISHSENSE_ADMIN_MODE_ENABLED", "true")
    monkeypatch.setenv("PHISHSENSE_ADMIN_USERNAME", "admin")
    monkeypatch.setenv("PHISHSENSE_ADMIN_PASSWORD", "secret")
    monkeypatch.setenv("PHISHSENSE_HISTORY_ENABLED", "true")
    monkeypatch.setenv("PHISHSENSE_HISTORY_DB_PATH", str(tmp_path / "history.db"))
    monkeypatch.setenv("PHISHSENSE_RATE_LIMIT_ENABLED", "false")
    monkeypatch.setattr(
        "app.main.generate_ai_assessment",
        lambda **kwargs: {
            "score": 88,
            "risk_level": "High",
            "red_flags": ["Impersonation signs", "Credential request"],
            "recommended_action": "Do not engage; report and verify via official channels.",
            "ai_explanation": "High likelihood of phishing based on impersonation and credential prompts.",
            "source": "ai",
        },
    )

    payload = {
        "sender": "support@micros0ft-login.com",
        "subject": "Urgent: Verify your account now",
        "body": "Your account will be suspended immediately. Log in and confirm your password now!",
        "url": "https://bit.ly/fake-login",
    }

    analyze_response = client.post("/analyze", json=payload)
    assert analyze_response.status_code == 200

    history_response = client.get("/admin/history", auth=("admin", "secret"))
    assert history_response.status_code == 200

    body = history_response.json()
    assert body["count"] >= 1
    first_item = body["items"][0]
    assert first_item["sender"] == payload["sender"]
    assert first_item["subject"] == payload["subject"]
    assert first_item["ai_explanation"] == "High likelihood of phishing based on impersonation and credential prompts."
    assert isinstance(first_item["rule_hits"], list)

    detail_response = client.get(f"/admin/history/{first_item['id']}", auth=("admin", "secret"))
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["id"] == first_item["id"]
    assert detail["recommended_action"]
    assert "rule_hits" in detail


def test_admin_history_returns_404_when_disabled(monkeypatch):
    client = TestClient(app)

    monkeypatch.setenv("PHISHSENSE_ADMIN_MODE_ENABLED", "true")
    monkeypatch.setenv("PHISHSENSE_ADMIN_USERNAME", "admin")
    monkeypatch.setenv("PHISHSENSE_ADMIN_PASSWORD", "secret")
    monkeypatch.setenv("PHISHSENSE_HISTORY_ENABLED", "false")

    response = client.get("/admin/history", auth=("admin", "secret"))
    assert response.status_code == 404
