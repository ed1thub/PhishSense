from typing import List, Tuple

from app.scoring_rules.common import extract_domain
from app.scoring_rules.config import RuleConfig


def score_domain(sender: str, url: str, config: RuleConfig) -> Tuple[int, List[str]]:
    score = 0
    red_flags: List[str] = []

    sender_domain = extract_domain(sender)
    url_domain = extract_domain(url)

    if sender_domain and any(char.isdigit() for char in sender_domain):
        score += 10
        red_flags.append("Sender domain contains unusual numeric lookalikes")

    if url_domain in config.shortener_domains:
        score += 15
        red_flags.append("Shortened URL detected")

    if sender_domain and url_domain and sender_domain not in url_domain:
        score += 20
        red_flags.append("Sender domain does not match linked domain")

    if url_domain.endswith(config.suspicious_tlds):
        score += 10
        red_flags.append("Suspicious top-level domain detected")

    return score, red_flags
