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
        return "AI explanation is unavailable because GEMINI_API_KEY is not configured."

    try:
        # Import lazily so SDK issues don't crash application startup.
        from google import genai

    except ImportError:
        logger.exception("Google GenAI SDK is not available")
        return "AI explanation is temporarily unavailable."

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
1. Explain in plain English why this email may be suspicious.
2. Mention the most important warning signs.
3. Recommend a safe next action for the user.
4. Keep the tone calm, clear, and concise.
5. Do not invent details that are not present.
        """.strip()

        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
        )

        if hasattr(response, "text") and response.text:
            return response.text.strip()

        return "AI explanation is temporarily unavailable."

    except Exception:
        logger.exception("Failed generating AI explanation")
        return "AI explanation is temporarily unavailable."