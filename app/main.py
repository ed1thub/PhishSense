from pathlib import Path
import logging

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.ai_analysis import generate_ai_explanation
from app.logging_config import configure_logging
from app.schemas import AnalysisResult, EmailInput
from app.scoring_rules import analyze_email
from app.settings import get_settings

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title=settings.app_name)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

ANALYZE_422_RESPONSE = {
    "description": "Validation error in request payload",
    "content": {
        "application/json": {
            "examples": {
                "empty_body": {
                    "summary": "Body is required",
                    "value": {
                        "detail": [
                            {
                                "type": "value_error",
                                "loc": ["body", "body"],
                                "msg": "Value error, Body is required and cannot be empty",
                                "input": "   ",
                                "ctx": {
                                    "error": "Body is required and cannot be empty",
                                },
                            }
                        ]
                    },
                },
                "invalid_url": {
                    "summary": "Unsupported URL scheme",
                    "value": {
                        "detail": [
                            {
                                "type": "value_error",
                                "loc": ["body", "url"],
                                "msg": "Value error, URL must start with http:// or https://",
                                "input": "ftp://example.com",
                                "ctx": {
                                    "error": "URL must start with http:// or https://",
                                },
                            }
                        ]
                    },
                },
            }
        }
    },
}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.post("/analyze", response_model=AnalysisResult, responses={422: ANALYZE_422_RESPONSE})
async def analyze(payload: EmailInput):
    logger.info("Analyze request received")

    scoring_result = analyze_email(
        sender=payload.sender,
        subject=payload.subject,
        body=payload.body,
        url=payload.url,
    )

    try:
        explanation = generate_ai_explanation(
            sender=payload.sender,
            subject=payload.subject,
            body=payload.body,
            url=payload.url,
            score=scoring_result["score"],
            risk_level=scoring_result["risk_level"],
            red_flags=scoring_result["red_flags"],
        )
    except Exception:
        logger.exception("Unexpected failure during AI explanation generation")
        explanation = "AI explanation is temporarily unavailable."

    return AnalysisResult(
        score=scoring_result["score"],
        risk_level=scoring_result["risk_level"],
        red_flags=scoring_result["red_flags"],
        ai_explanation=explanation,
        recommended_action=scoring_result["recommended_action"],
    )