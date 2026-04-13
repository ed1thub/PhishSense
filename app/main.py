from pathlib import Path
import logging

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.ai_analysis import generate_ai_explanation
from app.history_store import HistoryStore, model_to_dict
from app.logging_config import configure_logging
from app.rate_limit import RateLimiter
from app.schemas import AnalysisResult, EmailInput
from app.scoring_rules import analyze_email
from app.security import require_admin_user
from app.settings import get_settings

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title=settings.app_name)
rate_limiter = RateLimiter()
history_store: HistoryStore | None = None
history_store_path = ""

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


def get_history_store() -> HistoryStore | None:
    global history_store
    global history_store_path

    current_settings = get_settings()
    if not current_settings.history_enabled:
        return None

    if history_store is None or history_store_path != current_settings.history_db_path:
        history_store = HistoryStore(current_settings.history_db_path)
        history_store_path = current_settings.history_db_path

    return history_store


def reset_history_store_for_tests() -> None:
    global history_store
    global history_store_path
    history_store = None
    history_store_path = ""


def _client_identifier(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for", "")
    if forwarded_for:
        return forwarded_for.split(",", 1)[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


@app.middleware("http")
async def apply_rate_limit(request: Request, call_next):
    current_settings = get_settings()
    if (
        not current_settings.rate_limit_enabled
        or request.method != "POST"
        or request.url.path != "/analyze"
    ):
        return await call_next(request)

    key = _client_identifier(request)
    allowed, retry_after = rate_limiter.is_allowed(
        key=f"{request.url.path}:{key}",
        max_requests=current_settings.rate_limit_requests,
        window_seconds=current_settings.rate_limit_window_seconds,
    )

    if not allowed:
        logger.warning("Rate limit exceeded", extra={"client": key, "path": request.url.path})
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Too many requests. Please try again later.",
                "retry_after_seconds": retry_after,
            },
            headers={"Retry-After": str(retry_after)},
        )

    return await call_next(request)

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

    result = AnalysisResult(
        score=scoring_result["score"],
        risk_level=scoring_result["risk_level"],
        red_flags=scoring_result["red_flags"],
        rule_hits=scoring_result["rule_hits"],
        ai_explanation=explanation,
        recommended_action=scoring_result["recommended_action"],
    )

    store = get_history_store()
    if store is not None:
        try:
            store.save_analysis(
                sender=payload.sender,
                subject=payload.subject,
                url=payload.url,
                score=result.score,
                risk_level=result.risk_level,
                red_flags=result.red_flags,
                rule_hits=result.rule_hits,
                ai_explanation=result.ai_explanation,
                recommended_action=result.recommended_action,
            )
        except Exception:
            logger.exception("Failed to save analysis history")

    return result


@app.get("/admin")
async def admin_panel(admin_user: str = Depends(require_admin_user)):
    current_settings = get_settings()
    return {
        "message": "Admin mode enabled",
        "admin_user": admin_user,
        "rate_limit": {
            "enabled": current_settings.rate_limit_enabled,
            "requests": current_settings.rate_limit_requests,
            "window_seconds": current_settings.rate_limit_window_seconds,
        },
        "history": {
            "enabled": current_settings.history_enabled,
            "db_path": current_settings.history_db_path,
            "max_results": current_settings.history_max_results,
        },
    }


@app.get("/admin/history")
async def get_history(
    admin_user: str = Depends(require_admin_user),
    limit: int = Query(default=20, ge=1, le=200),
):
    del admin_user
    current_settings = get_settings()
    store = get_history_store()
    if store is None:
        raise HTTPException(status_code=404, detail="History storage is disabled")

    capped_limit = min(limit, current_settings.history_max_results)
    items = [model_to_dict(item) for item in store.list_recent(capped_limit)]
    return {"items": items, "count": len(items)}


@app.get("/admin/history/{analysis_id}")
async def get_history_item(analysis_id: int, admin_user: str = Depends(require_admin_user)):
    del admin_user
    store = get_history_store()
    if store is None:
        raise HTTPException(status_code=404, detail="History storage is disabled")

    item = store.get_by_id(analysis_id)
    if item is None:
        raise HTTPException(status_code=404, detail="History item not found")

    return model_to_dict(item)