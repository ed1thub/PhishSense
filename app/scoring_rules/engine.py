from typing import Any, Dict, List

from app.scoring_rules.config import load_rule_config
from app.scoring_rules.content import score_content
from app.scoring_rules.domain import score_domain
from app.scoring_rules.policy import clamp_score, recommended_action, resolve_risk_level


def analyze_email(sender: str, subject: str, body: str, url: str) -> Dict[str, Any]:
    config = load_rule_config()
    score = 0
    red_flags: List[str] = []
    rule_hits: List[Dict[str, Any]] = []

    content_score, content_flags, content_rule_hits = score_content(subject, body, config)
    domain_score, domain_flags, domain_rule_hits = score_domain(sender, url, config)

    score += content_score + domain_score
    red_flags.extend(content_flags)
    red_flags.extend(domain_flags)
    rule_hits.extend(content_rule_hits)
    rule_hits.extend(domain_rule_hits)

    score = clamp_score(score, config)
    risk_level = resolve_risk_level(score, config)

    if not red_flags:
        red_flags.append("No major rule-based phishing indicators were detected")

    return {
        "score": score,
        "risk_level": risk_level,
        "red_flags": red_flags,
        "rule_hits": rule_hits,
        "recommended_action": recommended_action(risk_level, config),
    }
