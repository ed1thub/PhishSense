import re
from urllib.parse import urlparse


URGENT_PATTERNS = [
    r"\burgent\b",
    r"\bimmediately\b",
    r"\bverify now\b",
    r"\bact now\b",
    r"\bsuspended\b",
    r"\baccount suspended\b",
    r"\bpayment failed\b",
]

CREDENTIAL_PATTERNS = [
    r"\bpassword\b",
    r"\blog in\b",
    r"\blogin\b",
    r"\bsign in\b",
    r"\bconfirm your account\b",
    r"\bverify your account\b",
]

FINANCIAL_PATTERNS = [
    r"\brefund\b",
    r"\binvoice\b",
    r"\bbank\b",
    r"\bpayment\b",
    r"\bprize\b",
    r"\bwinner\b",
]

SHORTENER_DOMAINS = {
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "goo.gl",
    "ow.ly",
    "is.gd",
    "buff.ly",
}


def extract_domain(value: str) -> str:
    value = value.strip().lower()
    if not value:
        return ""

    if "@" in value:
        return value.split("@")[-1]

    if value.startswith("http://") or value.startswith("https://"):
        parsed = urlparse(value)
        return (parsed.netloc or "").lower()

    return value


def contains_pattern(text: str, patterns: list[str]) -> bool:
    lowered = text.lower()
    return any(re.search(pattern, lowered) for pattern in patterns)


def analyze_email(sender: str, subject: str, body: str, url: str) -> dict:
    score = 0
    red_flags: list[str] = []

    combined = f"{subject}\n{body}"

    if contains_pattern(combined, URGENT_PATTERNS):
        score += 15
        red_flags.append("Urgent pressure language detected")

    if contains_pattern(combined, CREDENTIAL_PATTERNS):
        score += 20
        red_flags.append("Credential or account verification language detected")

    if contains_pattern(combined, FINANCIAL_PATTERNS):
        score += 10
        red_flags.append("Financial bait or money-related pressure detected")

    sender_domain = extract_domain(sender)
    url_domain = extract_domain(url)

    if sender_domain and any(char.isdigit() for char in sender_domain):
        score += 10
        red_flags.append("Sender domain contains unusual numeric lookalikes")

    if url_domain in SHORTENER_DOMAINS:
        score += 15
        red_flags.append("Shortened URL detected")

    if sender_domain and url_domain and sender_domain not in url_domain:
        score += 20
        red_flags.append("Sender domain does not match linked domain")

    suspicious_tlds = (".ru", ".xyz", ".top", ".click", ".shop")
    if url_domain.endswith(suspicious_tlds):
        score += 10
        red_flags.append("Suspicious top-level domain detected")

    exclamations = combined.count("!")
    if exclamations >= 3:
        score += 5
        red_flags.append("Excessive punctuation detected")

    if "attachment" in combined.lower() and ("enable macros" in combined.lower() or "download" in combined.lower()):
        score += 15
        red_flags.append("Suspicious attachment or download wording detected")

    score = min(score, 100)

    if score >= 60:
        risk_level = "High"
    elif score >= 30:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    if not red_flags:
        red_flags.append("No major rule-based phishing indicators were detected")

    recommended_action = {
        "High": "Do not click links or reply. Verify the message through the sender's official website or support channel.",
        "Medium": "Be cautious. Verify the sender and inspect links carefully before taking any action.",
        "Low": "No strong phishing indicators were found, but you should still verify unexpected requests independently.",
    }[risk_level]

    return {
        "score": score,
        "risk_level": risk_level,
        "red_flags": red_flags,
        "recommended_action": recommended_action,
    }