import logging
import json
import re
from typing import List

from app.settings import get_settings

logger = logging.getLogger(__name__)

MAX_SENDER_LEN = 320
MAX_SUBJECT_LEN = 300
MAX_BODY_LEN = 4000
MAX_URL_LEN = 2048
MAX_AI_RED_FLAGS = 10


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


def _extract_json_object(text: str) -> dict | None:
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None

    try:
        payload = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None

    return payload if isinstance(payload, dict) else None


def _sanitize_ai_assessment(payload: dict, fallback_result: dict) -> dict:
    score = payload.get("score", fallback_result["score"])
    try:
        score = int(score)
    except (TypeError, ValueError):
        score = fallback_result["score"]
    score = max(0, min(100, score))

    risk_level = payload.get("risk_level", "")
    if risk_level not in {"Low", "Medium", "High"}:
        if score >= 60:
            risk_level = "High"
        elif score >= 30:
            risk_level = "Medium"
        else:
            risk_level = "Low"

    red_flags = payload.get("red_flags", fallback_result["red_flags"])
    if not isinstance(red_flags, list):
        red_flags = fallback_result["red_flags"]
    red_flags = [str(flag).strip() for flag in red_flags if str(flag).strip()][:MAX_AI_RED_FLAGS]

    recommended_action = str(
        payload.get("recommended_action", fallback_result["recommended_action"])
    ).strip()
    if not recommended_action:
        recommended_action = fallback_result["recommended_action"]

    ai_explanation = str(payload.get("ai_explanation", "")).strip()
    if not ai_explanation:
        ai_explanation = _build_local_explanation(
            sender="",
            subject="",
            url="",
            score=score,
            risk_level=risk_level,
            red_flags=red_flags,
        )

    return {
        "score": score,
        "risk_level": risk_level,
        "red_flags": red_flags,
        "recommended_action": recommended_action,
        "ai_explanation": ai_explanation,
    }


def generate_ai_assessment(
    sender: str,
    subject: str,
    body: str,
    url: str,
    fallback_result: dict,
) -> dict:
    settings = get_settings()
    if not settings.gemini_api_key:
        return {
            "score": fallback_result["score"],
            "risk_level": fallback_result["risk_level"],
            "red_flags": fallback_result["red_flags"],
            "recommended_action": fallback_result["recommended_action"],
            "ai_explanation": _build_local_explanation(
                sender=sender,
                subject=subject,
                url=url,
                score=fallback_result["score"],
                risk_level=fallback_result["risk_level"],
                red_flags=fallback_result["red_flags"],
            ),
            "source": "fallback",
        }

    try:
        from google import genai
    except ImportError:
        logger.exception("Google GenAI SDK is not available")
        return {
            "score": fallback_result["score"],
            "risk_level": fallback_result["risk_level"],
            "red_flags": fallback_result["red_flags"],
            "recommended_action": fallback_result["recommended_action"],
            "ai_explanation": _build_local_explanation(
                sender=sender,
                subject=subject,
                url=url,
                score=fallback_result["score"],
                risk_level=fallback_result["risk_level"],
                red_flags=fallback_result["red_flags"],
            ),
            "source": "fallback",
        }

    try:
        safe_sender = _truncate(sender, MAX_SENDER_LEN)
        safe_subject = _truncate(subject, MAX_SUBJECT_LEN)
        safe_body = _truncate(body, MAX_BODY_LEN)
        safe_url = _truncate(url, MAX_URL_LEN)

        client = genai.Client(api_key=settings.gemini_api_key)

        prompt = f"""
You are a cybersecurity assistant analyzing a potentially suspicious email.

Use your own judgment to score phishing risk from 0 to 100 based on the email content.

Email:
Sender: {safe_sender}
Subject: {safe_subject}
Body: {safe_body}
URL: {safe_url}

Return STRICT JSON only (no markdown, no prose), with this exact shape:
{{
  "score": 0,
  "risk_level": "Low",
  "red_flags": ["..."],
  "recommended_action": "...",
  "ai_explanation": "..."
}}

Rules:
- score must be an integer 0-100
- risk_level must be one of: Low, Medium, High
- include 1 to 5 short red flags when applicable
- keep ai_explanation concise and professional
- do not invent facts not present in the email
        """.strip()

        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
        )

        response_text = getattr(response, "text", "") or ""
        parsed = _extract_json_object(response_text)
        if not parsed:
            logger.warning("Gemini returned non-JSON assessment; using fallback")
            return {
                "score": fallback_result["score"],
                "risk_level": fallback_result["risk_level"],
                "red_flags": fallback_result["red_flags"],
                "recommended_action": fallback_result["recommended_action"],
                "ai_explanation": _build_local_explanation(
                    sender=sender,
                    subject=subject,
                    url=url,
                    score=fallback_result["score"],
                    risk_level=fallback_result["risk_level"],
                    red_flags=fallback_result["red_flags"],
                ),
                "source": "fallback",
            }

        result = _sanitize_ai_assessment(parsed, fallback_result)
        result["source"] = "ai"
        return result

    except Exception:
        logger.exception("Failed generating AI assessment")
        return {
            "score": fallback_result["score"],
            "risk_level": fallback_result["risk_level"],
            "red_flags": fallback_result["red_flags"],
            "recommended_action": fallback_result["recommended_action"],
            "ai_explanation": _build_local_explanation(
                sender=sender,
                subject=subject,
                url=url,
                score=fallback_result["score"],
                risk_level=fallback_result["risk_level"],
                red_flags=fallback_result["red_flags"],
            ),
            "source": "fallback",
        }


def generate_ai_explanation(
    sender: str,
    subject: str,
    body: str,
    url: str,
    score: int,
    risk_level: str,
    red_flags: List[str],
) -> str:
    fallback_result = {
        "score": score,
        "risk_level": risk_level,
        "red_flags": red_flags,
        "recommended_action": "Verify through an official channel before taking any action.",
    }
    assessment = generate_ai_assessment(
        sender=sender,
        subject=subject,
        body=body,
        url=url,
        fallback_result=fallback_result,
    )
    return assessment["ai_explanation"]