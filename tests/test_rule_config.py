from app.scoring_rules.config import load_rule_config


def test_rule_config_loads_from_yaml_and_env_overrides(tmp_path, monkeypatch):
    rules_file = tmp_path / "rules.yaml"
    rules_file.write_text(
        """
urgent_patterns:
  - yaml-trigger
score_cap: 12
high_risk_threshold: 9
medium_risk_threshold: 4
""".strip()
    )

    monkeypatch.setenv("PHISHSENSE_RULES_FILE", str(rules_file))
    monkeypatch.setenv("PHISHSENSE_URGENT_PATTERNS", "env-trigger")
    monkeypatch.setenv("PHISHSENSE_SCORE_CAP", "7")

    config = load_rule_config()

    assert config.urgent_patterns == ("env-trigger",)
    assert config.score_cap == 7
    assert config.high_risk_threshold == 9
    assert config.medium_risk_threshold == 4
