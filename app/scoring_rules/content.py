from typing import Any, Dict, List, Tuple

from app.scoring_rules.common import contains_pattern
from app.scoring_rules.config import RuleConfig


def score_content(subject: str, body: str, config: RuleConfig) -> Tuple[int, List[str], List[Dict[str, Any]]]:
    score = 0
    red_flags: List[str] = []
    rule_hits: List[Dict[str, Any]] = []
    combined = f"{subject}\n{body}"
    lowered_combined = combined.lower()

    if contains_pattern(combined, config.urgent_patterns):
        score += 15
        red_flags.append("Urgent pressure language detected")
        rule_hits.append(
            {
                "rule_id": "content.urgent_language",
                "signal": "Urgent pressure language detected",
                "points": 15,
                "confidence": 0.72,
                "explanation": "The email uses urgency cues commonly seen in phishing pressure tactics.",
            }
        )

    if contains_pattern(combined, config.credential_patterns):
        score += 20
        red_flags.append("Credential or account verification language detected")
        rule_hits.append(
            {
                "rule_id": "content.credential_request",
                "signal": "Credential or account verification language detected",
                "points": 20,
                "confidence": 0.86,
                "explanation": "The message asks for login or account verification details, a high-risk phishing indicator.",
            }
        )

    if contains_pattern(combined, config.financial_patterns):
        score += 10
        red_flags.append("Financial bait or money-related pressure detected")
        rule_hits.append(
            {
                "rule_id": "content.financial_bait",
                "signal": "Financial bait or money-related pressure detected",
                "points": 10,
                "confidence": 0.64,
                "explanation": "Money-related hooks are often used to increase click-through in phishing campaigns.",
            }
        )

    if "attachment" in lowered_combined and ("enable macros" in lowered_combined or "download" in lowered_combined):
        score += 15
        red_flags.append("Suspicious attachment or download wording detected")
        rule_hits.append(
            {
                "rule_id": "content.suspicious_attachment",
                "signal": "Suspicious attachment or download wording detected",
                "points": 15,
                "confidence": 0.83,
                "explanation": "Attachment prompts involving downloads or macro enabling are a known malware delivery pattern.",
            }
        )

    exclamations = combined.count("!")
    if exclamations >= 3:
        score += 5
        red_flags.append("Excessive punctuation detected")
        rule_hits.append(
            {
                "rule_id": "content.excessive_punctuation",
                "signal": "Excessive punctuation detected",
                "points": 5,
                "confidence": 0.51,
                "explanation": "Excessive punctuation often indicates manipulative urgency, but can also appear in legitimate messages.",
            }
        )

    return score, red_flags, rule_hits
