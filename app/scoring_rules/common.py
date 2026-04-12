import re
from urllib.parse import urlparse


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


def contains_pattern(text: str, patterns: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(re.search(pattern, lowered) for pattern in patterns)
