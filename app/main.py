from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.ai_analysis import generate_ai_explanation
from app.schemas import AnalysisResult, EmailInput
from app.scoring import analyze_email

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title="PhishSense")

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analyze", response_model=AnalysisResult)
async def analyze(payload: EmailInput):
    scoring_result = analyze_email(
        sender=payload.sender,
        subject=payload.subject,
        body=payload.body,
        url=payload.url,
    )

    explanation = generate_ai_explanation(
        sender=payload.sender,
        subject=payload.subject,
        body=payload.body,
        url=payload.url,
        score=scoring_result["score"],
        risk_level=scoring_result["risk_level"],
        red_flags=scoring_result["red_flags"],
    )

    return AnalysisResult(
        score=scoring_result["score"],
        risk_level=scoring_result["risk_level"],
        red_flags=scoring_result["red_flags"],
        ai_explanation=explanation,
        recommended_action=scoring_result["recommended_action"],
    )