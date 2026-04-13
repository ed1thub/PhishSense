from typing import Any, Dict, List, Tuple

from app.scoring_rules.common import extract_domain
from app.scoring_rules.config import RuleConfig


def score_domain(sender: str, url: str, config: RuleConfig) -> Tuple[int, List[str], List[Dict[str, Any]]]:
    score = 0
    red_flags: List[str] = []
    rule_hits: List[Dict[str, Any]] = []

    sender_domain = extract_domain(sender)
    url_domain = extract_domain(url)

    if sender_domain and any(char.isdigit() for char in sender_domain):
        score += 10
        red_flags.append("Sender domain contains unusual numeric lookalikes")
        rule_hits.append(
            {
                "rule_id": "domain.numeric_lookalike",
                "signal": "Sender domain contains unusual numeric lookalikes",
                "points": 10,
                "confidence": 0.66,
                "explanation": "Numeric substitutions in domains can imitate trusted brands and are frequently abused in phishing.",
            }
        )

    if url_domain in config.shortener_domains:
        score += 15
        red_flags.append("Shortened URL detected")
        rule_hits.append(
            {
                "rule_id": "domain.shortened_url",
                "signal": "Shortened URL detected",
                "points": 15,
                "confidence": 0.74,
                "explanation": "Short links hide final destinations and reduce link transparency.",
            }
        )

    if sender_domain and url_domain and sender_domain not in url_domain:
        score += 20
        red_flags.append("Sender domain does not match linked domain")
        rule_hits.append(
            {
                "rule_id": "domain.sender_url_mismatch",
                "signal": "Sender domain does not match linked domain",
                "points": 20,
                "confidence": 0.89,
                "explanation": "Mismatch between sender identity and link destination is a strong phishing indicator.",
            }
        )

    if url_domain.endswith(config.suspicious_tlds):
        score += 10
        red_flags.append("Suspicious top-level domain detected")
        rule_hits.append(
            {
                "rule_id": "domain.suspicious_tld",
                "signal": "Suspicious top-level domain detected",
                "points": 10,
                "confidence": 0.61,
                "explanation": "The linked domain uses a TLD commonly associated with abuse in phishing campaigns.",
            }
        )

    return score, red_flags, rule_hits
