# PhishSense Developer README

## Overview

PhishSense is a FastAPI-based phishing analysis app that combines:

- AI-first scoring/analysis with Gemini in `app/ai_analysis.py`
- modular rule-based fallback detection in `app/scoring_rules/`
- AI explanation generation in `app/ai_analysis.py`
- a modern responsive web frontend (`app/templates/index.html`, `static/app.js`, `static/style.css`)

The API includes security and operations features:

- request validation with structured 422 responses
- in-memory rate limiting for `POST /analyze`
- optional admin mode with HTTP Basic authentication
- persisted analysis history via SQLite
- per-rule explainability output (`rule_hits`) with confidence and rationale
- polished AI explanation output with Gemini as the primary path and a local rule-based fallback for transient Gemini failures or outages

Core endpoint: `POST /analyze`

## Frontend Notes

- `app/templates/index.html` defines a two-panel layout (input and results) with a semantic hero header.
- `static/style.css` contains the visual design system (CSS variables, typography, cards, buttons, and responsive breakpoints).
- `static/app.js` preserves all interaction logic for sample loading, validation messages, loading state, and result rendering.
- Responsive behavior is handled in CSS with tablet and mobile breakpoints so input and results stack cleanly on smaller screens.
- Motion is intentionally subtle and includes reduced-motion support for accessibility.

## Architecture

- `app/main.py`: FastAPI app, routes, static mount, template rendering
- `app/scoring_rules/engine.py`: deterministic phishing scoring fallback orchestration
- `app/scoring_rules/config.py`: YAML/env-driven rule configuration loader
- `app/ai_analysis.py`: Gemini-based explanation generation with safe fallback handling
- `app/schemas.py`: request/response models and validation
- `app/rate_limit.py`: in-memory per-client throttling
- `app/security.py`: admin authentication dependency
- `app/history_store.py`: SQLite persistence for saved analyses
- `app/settings.py`: centralized env-backed runtime config
- `tests/`: scoring, config, validation, and settings tests

See `PROJECT_STRUCTURE.md` for a complete folder-by-folder map.

## Detection Rules

Current signals include:

- urgency/pressure language
- credential request patterns
- financial bait language
- numeric-lookalike sender domains
- URL shorteners
- sender and URL domain mismatch
- suspicious TLDs (`.ru`, `.xyz`, `.top`, `.click`, `.shop`)
- excessive punctuation
- suspicious attachment/download wording

## Local Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `.env`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Run app:

```bash
uvicorn app.main:app --reload
```

Run tests:

```bash
python -m pytest -q
```

## API Contract

Request (`POST /analyze`):

```json
{
  "sender": "support@micros0ft-login.com",
  "subject": "Urgent: Verify your account now",
  "body": "Your account has been suspended...",
  "url": "https://bit.ly/security-check"
}
```

Response:

```json
{
  "score": 80,
  "risk_level": "High",
  "red_flags": [
    "Urgent pressure language detected",
    "Credential or account verification language detected"
  ],
  "rule_hits": [
    {
      "rule_id": "content.credential_request",
      "signal": "Credential or account verification language detected",
      "points": 20,
      "confidence": 0.86,
      "explanation": "The message asks for login or account verification details, a high-risk phishing indicator."
    }
  ],
  "ai_explanation": "...",
  "recommended_action": "Do not click links or reply..."
}
```

Note: `ai_explanation` is always populated. The intended product experience is Gemini-backed explanations; when Gemini returns a transient failure such as 503 UNAVAILABLE, the app returns a local rule-based explanation instead of a generic unavailable message.

Admin endpoints:

- `GET /admin`
- `GET /admin/history`
- `GET /admin/history/{id}`

## Deployment Notes (Render)

- Build: `pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Required env: `GEMINI_API_KEY` (for the intended Gemini-backed explanations)
- Optional env: `PHISHSENSE_RATE_LIMIT_*`, `PHISHSENSE_ADMIN_*`, `PHISHSENSE_HISTORY_*`

Important compatibility note:

- Template rendering should use keyword args for Starlette compatibility:
  - `templates.TemplateResponse(request=request, name="index.html")`

## Known Limitations

- Rule-based logic can miss novel phishing patterns.
- AI explanations are based on Gemini as the primary experience, with a deterministic local fallback for transient Gemini failures or outages.
- In-memory rate limiting is per-instance and resets on restart.
- SQLite history is local to instance storage unless backed by persistent volume.
- This is an educational project, not a complete enterprise email security platform.
