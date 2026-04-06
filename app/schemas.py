from pydantic import BaseModel


class EmailInput(BaseModel):
    sender: str = ""
    subject: str = ""
    body: str
    url: str = ""


class AnalysisResult(BaseModel):
    score: int
    risk_level: str
    red_flags: list[str]
    ai_explanation: str
    recommended_action: str