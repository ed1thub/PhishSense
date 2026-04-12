from app.scoring_rules.config import RuleConfig


def clamp_score(score: int, config: RuleConfig) -> int:
    return min(score, config.score_cap)


def resolve_risk_level(score: int, config: RuleConfig) -> str:
    if score >= config.high_risk_threshold:
        return "High"
    if score >= config.medium_risk_threshold:
        return "Medium"
    return "Low"


def recommended_action(risk_level: str, config: RuleConfig) -> str:
    return config.risk_actions[risk_level]
