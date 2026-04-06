from app.scoring import analyze_email


def test_high_risk_email():
    result = analyze_email(
        sender="support@micros0ft-login.com",
        subject="Urgent: Verify your account now",
        body="Your account will be suspended immediately. Log in and confirm your password now!",
        url="https://bit.ly/fake-login",
    )

    assert result["score"] >= 60
    assert result["risk_level"] == "High"
    assert len(result["red_flags"]) >= 2