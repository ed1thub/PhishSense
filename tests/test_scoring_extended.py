import pytest

from app.scoring_rules import analyze_email


@pytest.mark.parametrize(
    "sender,subject,body,url,expected_risk,max_score",
    [
        (
            "newsletter@university.edu",
            "Campus event reminder",
            "The student fair starts at 3 PM in Building A.",
            "",
            "Low",
            25,
        ),
        (
            "alerts@company.com",
            "Security notice",
            "Please review the monthly login report in the employee portal.",
            "https://portal.company.com/security-report",
            "Low",
            25,
        ),
        (
            "help@bank.com",
            "Urgent fraud awareness training",
            "Urgent notice: complete awareness training this week with your manager.",
            "https://bank.com/training",
            "Low",
            29,
        ),
    ],
)
def test_benign_and_false_positive_like_emails_stay_low(sender, subject, body, url, expected_risk, max_score):
    result = analyze_email(sender=sender, subject=subject, body=body, url=url)

    assert result["risk_level"] == expected_risk
    assert result["score"] <= max_score


@pytest.mark.parametrize(
    "sender,subject,body,url",
    [
        (
            "support@micros0ft-login.com",
            "Urgent: Verify your account now",
            "Your account is suspended immediately. Log in now and confirm your password.",
            "https://bit.ly/fake-login",
        ),
        (
            "billing@secure-paypa1.com",
            "Payment failed - act now!!!",
            "Payment failed. Verify your account now, sign in, and update your bank details immediately!!!",
            "https://secure-paypa1.top/verify",
        ),
    ],
)
def test_obvious_phishing_emails_are_high_risk(sender, subject, body, url):
    result = analyze_email(sender=sender, subject=subject, body=body, url=url)

    assert result["risk_level"] == "High"
    assert result["score"] >= 60
    assert len(result["red_flags"]) >= 3


def test_missing_url_does_not_trigger_domain_mismatch():
    result = analyze_email(
        sender="updates@service.com",
        subject="Weekly digest",
        body="Your weekly summary is ready in the dashboard.",
        url="",
    )

    assert result["risk_level"] == "Low"
    assert "Sender domain does not match linked domain" not in result["red_flags"]


def test_mismatched_domains_are_flagged():
    result = analyze_email(
        sender="security@paypal.com",
        subject="Security check",
        body="Please review account activity in your dashboard.",
        url="https://paypa1-security-check.com/login",
    )

    assert "Sender domain does not match linked domain" in result["red_flags"]
    assert result["score"] >= 20


def test_triggered_rules_include_confidence_and_explanation_output():
    result = analyze_email(
        sender="support@micros0ft-login.com",
        subject="Urgent: Verify your account now",
        body="Your account is suspended immediately. Log in now and confirm your password.",
        url="https://bit.ly/fake-login",
    )

    assert result["rule_hits"]
    for hit in result["rule_hits"]:
        assert "rule_id" in hit
        assert "signal" in hit
        assert "points" in hit
        assert "confidence" in hit
        assert "explanation" in hit
        assert 0.0 <= hit["confidence"] <= 1.0


def test_edge_case_attachment_macro_language_detected():
    result = analyze_email(
        sender="hr@company.com",
        subject="Document review",
        body="Please open the attachment and enable macros to download the latest form.",
        url="https://company.com/forms",
    )

    assert "Suspicious attachment or download wording detected" in result["red_flags"]
    assert result["score"] >= 15


def test_edge_case_excessive_punctuation_detected():
    result = analyze_email(
        sender="notice@service.com",
        subject="Important update!!!",
        body="Please review this announcement!!!",
        url="https://service.com/notice",
    )

    assert "Excessive punctuation detected" in result["red_flags"]
    assert result["score"] >= 5
