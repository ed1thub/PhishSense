from typing import List, Tuple

from app.scoring_rules.common import contains_pattern
from app.scoring_rules.config import RuleConfig


def score_content(subject: str, body: str, config: RuleConfig) -> Tuple[int, List[str]]:
    score = 0
    red_flags: List[str] = []
    combined = f"{subject}\n{body}"
    lowered_combined = combined.lower()

    if contains_pattern(combined, config.urgent_patterns):
        score += 15
        red_flags.append("Urgent pressure language detected")

    if contains_pattern(combined, config.credential_patterns):
        score += 20
        red_flags.append("Credential or account verification language detected")

    if contains_pattern(combined, config.financial_patterns):
        score += 10
        red_flags.append("Financial bait or money-related pressure detected")

    if "attachment" in lowered_combined and ("enable macros" in lowered_combined or "download" in lowered_combined):
        score += 15
        red_flags.append("Suspicious attachment or download wording detected")

    exclamations = combined.count("!")
    if exclamations >= 3:
        score += 5
        red_flags.append("Excessive punctuation detected")

    return score, red_flags
