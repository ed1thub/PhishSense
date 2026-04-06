import os

from dotenv import load_dotenv
from google import genai

load_dotenv()


def generate_ai_explanation(
    sender: str,
    subject: str,
    body: str,
    url: str,
    score: int,
    risk_level: str,
    red_flags: list[str],
) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Gemini API key not found. Add GEMINI_API_KEY to your .env file."

    try:
        client = genai.Client(api_key=api_key)

        flags_text = "\n- ".join(red_flags)

        prompt = f"""
You are a cybersecurity assistant helping analyze a suspicious email.

A rule-based phishing detector has already scored this email.

Sender: {sender}
Subject: {subject}
Body: {body}
URL: {url}

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
            model="gemini-2.5-flash",
            contents=prompt,
        )

        if hasattr(response, "text") and response.text:
            return response.text.strip()

        return "Gemini returned an empty response."

    except Exception as exc:
        return f"AI explanation unavailable right now: {exc}"