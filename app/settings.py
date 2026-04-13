import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str
    log_level: str
    gemini_api_key: str
    gemini_model: str
    rules_file: str
    rate_limit_enabled: bool
    rate_limit_requests: int
    rate_limit_window_seconds: int
    admin_mode_enabled: bool
    admin_username: str
    admin_password: str
    history_enabled: bool
    history_db_path: str
    history_max_results: int


def _to_bool(value: str, default: bool) -> bool:
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return default


def _to_int(value: str, default: int) -> int:
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError:
        return default


def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("PHISHSENSE_APP_NAME", "PhishSense"),
        log_level=os.getenv("PHISHSENSE_LOG_LEVEL", "INFO"),
        gemini_api_key=os.getenv("GEMINI_API_KEY", "").strip(),
        gemini_model=os.getenv("PHISHSENSE_GEMINI_MODEL", "gemini-2.5-flash"),
        rules_file=os.getenv("PHISHSENSE_RULES_FILE", "").strip(),
        rate_limit_enabled=_to_bool(os.getenv("PHISHSENSE_RATE_LIMIT_ENABLED"), True),
        rate_limit_requests=max(1, _to_int(os.getenv("PHISHSENSE_RATE_LIMIT_REQUESTS"), 60)),
        rate_limit_window_seconds=max(1, _to_int(os.getenv("PHISHSENSE_RATE_LIMIT_WINDOW_SECONDS"), 60)),
        admin_mode_enabled=_to_bool(os.getenv("PHISHSENSE_ADMIN_MODE_ENABLED"), False),
        admin_username=os.getenv("PHISHSENSE_ADMIN_USERNAME", "").strip(),
        admin_password=os.getenv("PHISHSENSE_ADMIN_PASSWORD", "").strip(),
        history_enabled=_to_bool(os.getenv("PHISHSENSE_HISTORY_ENABLED"), True),
        history_db_path=os.getenv("PHISHSENSE_HISTORY_DB_PATH", "phishsense_history.db").strip(),
        history_max_results=max(1, _to_int(os.getenv("PHISHSENSE_HISTORY_MAX_RESULTS"), 100)),
    )
