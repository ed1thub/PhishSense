# PhishSense Deployment Guide

This guide covers production-minded deployment for the current architecture.

## Deployment Target

PhishSense is designed as a FastAPI web service and is currently configured for Render via [render.yaml](render.yaml).

Frontend note:

- The web UI is server-rendered from `app/templates/index.html` and serves static assets from `static/`.
- No frontend build pipeline is required for deployment.

## Render Deployment

1. Push latest code to GitHub.
2. In Render, create a new Web Service from this repository.
3. Confirm service settings:
- Environment: `Python`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Set environment variables (below).

## Docker Deployment

### Build and Run (Single Container)

```bash
docker build -t phishsense .
docker run --rm -p 8000:8000 --env-file .env phishsense
```

### Run with Docker Compose

```bash
docker compose up --build
```

Compose details:

- Maps port `8000:8000`
- Loads environment variables from `.env`
- Persists SQLite history at `/data/phishsense_history.db` via volume `phishsense_data`

Stop compose services:

```bash
docker compose down
```

## Required Environment Variables

`GEMINI_API_KEY`: required for the intended Gemini-backed explanation experience. If Gemini returns a transient error such as 503 UNAVAILABLE, the app uses a local rule-based explanation fallback for resilience.

## Recommended Environment Variables

### App and Logging
- In production, configure `GEMINI_API_KEY` so the AI explanation is Gemini-backed.
- `PHISHSENSE_APP_NAME` (default: `PhishSense`)
- `PHISHSENSE_LOG_LEVEL` (default: `INFO`)

### Rate Limiting
- `PHISHSENSE_RATE_LIMIT_ENABLED` (default: `true`)
- `PHISHSENSE_RATE_LIMIT_REQUESTS` (default: `60`)
- `PHISHSENSE_RATE_LIMIT_WINDOW_SECONDS` (default: `60`)

### Admin Mode
- `PHISHSENSE_ADMIN_MODE_ENABLED` (default: `false`)
- `PHISHSENSE_ADMIN_USERNAME`
- `PHISHSENSE_ADMIN_PASSWORD`

### History Storage
- `PHISHSENSE_HISTORY_ENABLED` (default: `true`)
- `PHISHSENSE_HISTORY_DB_PATH` (default: `phishsense_history.db`)
- `PHISHSENSE_HISTORY_MAX_RESULTS` (default: `100`)

### Scoring Rules
- `PHISHSENSE_RULES_FILE` (optional custom YAML)
- or rule-specific overrides such as `PHISHSENSE_URGENT_PATTERNS`

## Security Notes

- Keep `.env` out of source control.
- Use strong credentials for admin mode.
- Keep admin mode disabled unless needed.
- Treat `/admin` and `/admin/history` as operational endpoints.

## Persistence Notes

- Default history backend is SQLite.
- On ephemeral containers, local files may be lost on restart/redeploy.
- For durable history, mount persistent storage or move to an external database.

## Verification Checklist

After deploy, verify:

1. `GET /` returns the UI.
2. `POST /analyze` returns score + explainability (`rule_hits`) and a populated `ai_explanation`.
3. Flagged indicators show severity counts and only reveal indicator details after clicking a severity tab.
4. UI remains usable on mobile and desktop with responsive stacked layout on narrow screens.
5. Rate limiting returns `429` when threshold is exceeded.
6. Admin mode is inaccessible when disabled.
7. Admin mode requires Basic auth when enabled.
8. History endpoints behave correctly when history is enabled.
