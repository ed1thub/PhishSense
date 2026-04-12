import re
from typing import List, Literal

from pydantic import BaseModel, Field, field_validator


class EmailInput(BaseModel):
    sender: str = Field(default="", max_length=320)
    subject: str = Field(default="", max_length=300)
    body: str = Field(..., max_length=20000)
    url: str = Field(default="", max_length=2048)

    @field_validator("sender", "subject", "body", "url", mode="before")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        if value is None:
            return ""
        return str(value).strip()

    @field_validator("body")
    @classmethod
    def validate_body(cls, value: str) -> str:
        if not value:
            raise ValueError("Body is required and cannot be empty")
        return value

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        if not value:
            return value
        if not (value.startswith("http://") or value.startswith("https://")):
            raise ValueError("URL must start with http:// or https://")
        return value

    @field_validator("sender")
    @classmethod
    def validate_sender(cls, value: str) -> str:
        if not value:
            return value
        # Accept either email-like sender strings or domain-only sender values.
        email_like = re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value)
        domain_like = re.match(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", value)
        if not email_like and not domain_like:
            raise ValueError("Sender must be an email address or a domain")
        return value


class AnalysisResult(BaseModel):
    score: int = Field(ge=0, le=100)
    risk_level: Literal["Low", "Medium", "High"]
    red_flags: List[str]
    ai_explanation: str
    recommended_action: str