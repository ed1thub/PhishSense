from __future__ import annotations

import os
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from app.settings import get_settings

try:
    import yaml
except ImportError:  # pragma: no cover - dependency is listed in requirements.txt
    yaml = None

logger = logging.getLogger(__name__)


DEFAULT_URGENT_PATTERNS = (
    r"\burgent\b",
    r"\bimmediately\b",
    r"\bverify now\b",
    r"\bact now\b",
    r"\bsuspended\b",
    r"\baccount suspended\b",
    r"\bpayment failed\b",
)

DEFAULT_CREDENTIAL_PATTERNS = (
    r"\bpassword\b",
    r"\blog in\b",
    r"\blogin\b",
    r"\bsign in\b",
    r"\bconfirm your account\b",
    r"\bverify your account\b",
)

DEFAULT_FINANCIAL_PATTERNS = (
    r"\brefund\b",
    r"\binvoice\b",
    r"\bbank\b",
    r"\bpayment\b",
    r"\bprize\b",
    r"\bwinner\b",
)

DEFAULT_SHORTENER_DOMAINS = frozenset(
    {
        "bit.ly",
        "tinyurl.com",
        "t.co",
        "goo.gl",
        "ow.ly",
        "is.gd",
        "buff.ly",
    }
)

DEFAULT_SUSPICIOUS_TLDS = (".ru", ".xyz", ".top", ".click", ".shop")
DEFAULT_SCORE_CAP = 100
DEFAULT_HIGH_RISK_THRESHOLD = 60
DEFAULT_MEDIUM_RISK_THRESHOLD = 30
DEFAULT_RISK_ACTIONS = {
    "High": "Do not click links or reply. Verify the message through the sender's official website or support channel.",
    "Medium": "Be cautious. Verify the sender and inspect links carefully before taking any action.",
    "Low": "No strong phishing indicators were found, but you should still verify unexpected requests independently.",
}

DEFAULT_RULES_FILE = Path(__file__).with_name("rules.yaml")


@dataclass(frozen=True)
class RuleConfig:
    urgent_patterns: tuple[str, ...]
    credential_patterns: tuple[str, ...]
    financial_patterns: tuple[str, ...]
    shortener_domains: frozenset[str]
    suspicious_tlds: tuple[str, ...]
    score_cap: int
    high_risk_threshold: int
    medium_risk_threshold: int
    risk_actions: dict[str, str]


def _to_patterns(value: Any, fallback: tuple[str, ...]) -> tuple[str, ...]:
    if value is None:
        return fallback
    if isinstance(value, str):
        items = [item.strip() for item in value.replace("\n", ",").split(",")]
        filtered = tuple(item for item in items if item)
        return filtered if filtered else fallback
    if isinstance(value, list):
        filtered = tuple(str(item).strip() for item in value if str(item).strip())
        return filtered if filtered else fallback
    return fallback


def _to_domains(value: Any, fallback: frozenset[str]) -> frozenset[str]:
    return frozenset(_to_patterns(value, tuple(fallback)))


def _to_int(value: Any, fallback: int) -> int:
    if value is None or value == "":
        return fallback
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _load_yaml_rules(path: Path) -> Mapping[str, Any]:
    if not path.exists():
        return {}
    if yaml is None:
        logger.warning("Skipping YAML rules file because PyYAML is unavailable", extra={"path": str(path)})
        return {}

    try:
        with path.open("r", encoding="utf-8") as file_handle:
            data = yaml.safe_load(file_handle)
    except Exception:
        logger.exception("Failed to load YAML rules file", extra={"path": str(path)})
        return {}

    if isinstance(data, dict):
        return data
    return {}


def load_rule_config() -> RuleConfig:
    settings = get_settings()
    yaml_path = settings.rules_file
    config_source: Mapping[str, Any] = {}

    if yaml_path:
        config_source = _load_yaml_rules(Path(yaml_path).expanduser())
    elif DEFAULT_RULES_FILE.exists():
        config_source = _load_yaml_rules(DEFAULT_RULES_FILE)

    risk_actions_source = config_source.get("risk_actions", {})
    if not isinstance(risk_actions_source, dict):
        risk_actions_source = {}

    return RuleConfig(
        urgent_patterns=_to_patterns(
            os.getenv("PHISHSENSE_URGENT_PATTERNS", config_source.get("urgent_patterns")),
            DEFAULT_URGENT_PATTERNS,
        ),
        credential_patterns=_to_patterns(
            os.getenv("PHISHSENSE_CREDENTIAL_PATTERNS", config_source.get("credential_patterns")),
            DEFAULT_CREDENTIAL_PATTERNS,
        ),
        financial_patterns=_to_patterns(
            os.getenv("PHISHSENSE_FINANCIAL_PATTERNS", config_source.get("financial_patterns")),
            DEFAULT_FINANCIAL_PATTERNS,
        ),
        shortener_domains=_to_domains(
            os.getenv("PHISHSENSE_SHORTENER_DOMAINS", config_source.get("shortener_domains")),
            DEFAULT_SHORTENER_DOMAINS,
        ),
        suspicious_tlds=_to_patterns(
            os.getenv("PHISHSENSE_SUSPICIOUS_TLDS", config_source.get("suspicious_tlds")),
            DEFAULT_SUSPICIOUS_TLDS,
        ),
        score_cap=_to_int(os.getenv("PHISHSENSE_SCORE_CAP", config_source.get("score_cap")), DEFAULT_SCORE_CAP),
        high_risk_threshold=_to_int(
            os.getenv("PHISHSENSE_HIGH_RISK_THRESHOLD", config_source.get("high_risk_threshold")),
            DEFAULT_HIGH_RISK_THRESHOLD,
        ),
        medium_risk_threshold=_to_int(
            os.getenv("PHISHSENSE_MEDIUM_RISK_THRESHOLD", config_source.get("medium_risk_threshold")),
            DEFAULT_MEDIUM_RISK_THRESHOLD,
        ),
        risk_actions={
            "High": os.getenv("PHISHSENSE_HIGH_ACTION", risk_actions_source.get("High", DEFAULT_RISK_ACTIONS["High"])),
            "Medium": os.getenv("PHISHSENSE_MEDIUM_ACTION", risk_actions_source.get("Medium", DEFAULT_RISK_ACTIONS["Medium"])),
            "Low": os.getenv("PHISHSENSE_LOW_ACTION", risk_actions_source.get("Low", DEFAULT_RISK_ACTIONS["Low"])),
        },
    )
