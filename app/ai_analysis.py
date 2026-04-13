import logging
from typing import List

from app.settings import get_settings

logger = logging.getLogger(__name__)

MAX_SENDER_LEN = 320
MAX_SUBJECT_LEN = 300
MAX_BODY_LEN = 4000
MAX_URL_LEN = 2048
MAX_FLAGS = 12
MAX_FLAG_LEN = 300


def _truncate(value: str, limit: int) -> str:
    value = value.strip()
    if len(value) <= limit:
        return value
    return f"{value[: limit - 3]}..."


def _build_local_explanation(
    sender: str,
    subject: str,
    url: str,
    score: int,
    risk_level: str,
    red_flags: List[str],
) -> str:
    lines = [f"Backup assessment: This email scored {score}/100 and was labeled {risk_level} risk."]

    if red_flags:
        lines.append("Why it looks suspicious:")
        lines.extend(f"- {flag}" for flag in red_flags[:5])
    else:
        lines.append("No major rule-based phishing indicators were detected.")

    if sender:
        lines.append(f"Sender: {sender}.")
    if subject:
        lines.append(f"Subject: {subject}.")
    if url:
        lines.append(f"Link: {url}.")

    lines.append(
        "Recommended next step: verify the request through a trusted official channel before clicking, replying, or entering any information."
    )
    lines.append("This local explanation is shown only if Gemini is unavailable.")
    return "\n".join(lines)


def generate_ai_explanation(
    sender: str,
    subject: str,
    body: str,
    url: str,
    score: int,
    risk_level: str,
    red_flags: List[str],
) -> str:
    settings = get_settings()
    if not settings.gemini_api_key:
        return _build_local_explanation(sender, subject, url, score, risk_level, red_flags)

    try:
        # Import lazily so SDK issues don't crash application startup.
        from google import genai

    except ImportError:
        logger.exception("Google GenAI SDK is not available")
        return _build_local_explanation(sender, subject, url, score, risk_level, red_flags)

    try:
        safe_sender = _truncate(sender, MAX_SENDER_LEN)
        safe_subject = _truncate(subject, MAX_SUBJECT_LEN)
        safe_body = _truncate(body, MAX_BODY_LEN)
        safe_url = _truncate(url, MAX_URL_LEN)
        safe_flags = [_truncate(flag, MAX_FLAG_LEN) for flag in red_flags[:MAX_FLAGS]]

        client = genai.Client(api_key=settings.gemini_api_key)

        flags_text = "\n- ".join(safe_flags) if safe_flags else "No significant red flags identified"

        prompt = f"""
You are a cybersecurity assistant helping analyze a suspicious email.

A rule-based phishing detector has already scored this email.

Sender: {safe_sender}
Subject: {safe_subject}
Body: {safe_body}
URL: {safe_url}

Phishing score: {score}/100
Risk level: {risk_level}
Detected red flags:
- {flags_text}

Your task:
1. Write a polished, concise explanation in plain English.
2. Mention the most important warning signs.
3. Recommend a safe next action for the user.
4. Keep the tone calm, clear, and professional.
5. Do not invent details that are not present.
        """.strip()

        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
        )

        if hasattr(response, "text") and response.text:
            return response.text.strip()

        return _build_local_explanation(sender, subject, url, score, risk_level, red_flags)

    except Exception:
        logger.exception("Failed generating AI explanation")
        return _build_local_explanation(sender, subject, url, score, risk_level, red_flags)