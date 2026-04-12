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


def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("PHISHSENSE_APP_NAME", "PhishSense"),
        log_level=os.getenv("PHISHSENSE_LOG_LEVEL", "INFO"),
        gemini_api_key=os.getenv("GEMINI_API_KEY", "").strip(),
        gemini_model=os.getenv("PHISHSENSE_GEMINI_MODEL", "gemini-2.5-flash"),
        rules_file=os.getenv("PHISHSENSE_RULES_FILE", "").strip(),
    )
