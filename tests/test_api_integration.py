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

    monkeypatch.setattr("app.main.generate_ai_explanation", lambda **kwargs: "Mocked AI explanation")

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
        "ai_explanation",
        "recommended_action",
    }
    assert data["risk_level"] in {"Low", "Medium", "High"}
    assert isinstance(data["score"], int)
    assert isinstance(data["red_flags"], list)
    assert data["ai_explanation"] == "Mocked AI explanation"


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

    monkeypatch.setattr("app.main.generate_ai_explanation", raise_ai_error)

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
    assert data["ai_explanation"] == "AI explanation is temporarily unavailable."
