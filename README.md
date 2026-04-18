# PhishSense

PhishSense is a FastAPI web app that analyzes suspicious emails with Gemini-backed AI-generated scoring and explanations, with rule-based fallback for resilience.

## What It Does

- Scores emails from 0 to 100 using AI risk judgment
- Labels risk as Low, Medium, or High
- Shows detected red flags
- Highlights flagged indicators with severity labels (Critical, Warning, Notice)
- Shows indicator details only when users click severity tabs (Critical, Warning, Notice)
- Suggests a safe next action
- Generates a polished plain-English explanation with Gemini as the primary experience, with a local fallback for transient Gemini outages or 503s
- Validates user input and returns field-level 422 errors for bad payloads
- Applies per-client rate limiting on analysis requests
- Supports optional admin mode with authenticated operational endpoints
- Persists analysis history (SQLite by default) for admin review
- Provides a modern responsive web UI optimized for desktop and mobile screens
- Uses universal UI tuning for Android, iOS, Windows, and macOS (safe areas, touch targets, and reduced-motion support)

## Built With

- Python, FastAPI, Uvicorn
- HTML, CSS, JavaScript
- Google Gen AI SDK (Gemini)

## Quick Start

```bash
git clone https://github.com/ed1thub/PhishSense.git
cd PhishSense
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Run locally:

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

Run tests:

```bash
python -m pytest -q
```

## Docker Quick Start

Build and run with Docker Compose:

```bash
docker-compose up --build
```

Open `http://127.0.0.1:8000`.

Stop containers:

```bash
docker-compose down
```

Run as a single Docker container:

```bash
docker build -t phishsense .
docker run --rm -p 8000:8000 --env-file .env phishsense
```

## Configuration

### Core Settings

- `GEMINI_API_KEY`: Gemini API key used for AI explanation generation and the main AI experience
- `PHISHSENSE_GEMINI_MODEL`: Gemini model name (default: `gemini-2.5-flash`)
- `PHISHSENSE_LOG_LEVEL`: Backend logging level (default: `INFO`)
- `PHISHSENSE_APP_NAME`: FastAPI app title shown in OpenAPI docs
- `PHISHSENSE_RATE_LIMIT_ENABLED`: Enable or disable API rate limiting for `POST /analyze` (default: `true`)
- `PHISHSENSE_RATE_LIMIT_REQUESTS`: Max requests allowed per client in window (default: `60`)
- `PHISHSENSE_RATE_LIMIT_WINDOW_SECONDS`: Rate-limit window in seconds (default: `60`)
- `PHISHSENSE_ADMIN_MODE_ENABLED`: Enables secure admin endpoint access (default: `false`)
- `PHISHSENSE_ADMIN_USERNAME`: Username for HTTP Basic authentication on `/admin`
- `PHISHSENSE_ADMIN_PASSWORD`: Password for HTTP Basic authentication on `/admin`
- `PHISHSENSE_HISTORY_ENABLED`: Enables saving analysis history (default: `true`)
- `PHISHSENSE_HISTORY_DB_PATH`: SQLite database path for saved analyses (default: `phishsense_history.db`)
- `PHISHSENSE_HISTORY_MAX_RESULTS`: Max history rows returned in admin history listing (default: `100`)

### Scoring Rule Configuration

- Set `PHISHSENSE_RULES_FILE` to a YAML file, or edit [app/scoring_rules/rules.yaml](app/scoring_rules/rules.yaml#L1)
- Override individual values with env vars like `PHISHSENSE_URGENT_PATTERNS`, `PHISHSENSE_SCORE_CAP`, or `PHISHSENSE_HIGH_RISK_THRESHOLD`

## API

### POST /analyze

Request body:

- `sender` (optional)
- `subject` (optional)
- `body` (required)
- `url` (optional, must start with `http://` or `https://`)

Response includes:

- `score`
- `risk_level`
- `red_flags`
- `rule_hits` (fallback explainability details when rule-based backup is used)
- `ai_explanation` (Gemini output when available; local fallback during transient Gemini errors or outages)
- `recommended_action`

Each `rule_hits` item includes:

- `rule_id`
- `signal`
- `points`
- `confidence` (0.0 to 1.0)
- `explanation`

Validation behavior:

- Invalid inputs return HTTP 422
- Response includes `detail` entries with field-specific error messages

Rate limiting behavior:

- `POST /analyze` is rate limited per client IP
- Exceeded limits return HTTP 429 with `Retry-After` and `retry_after_seconds`

Admin mode behavior:

- `GET /admin` is hidden unless `PHISHSENSE_ADMIN_MODE_ENABLED=true`
- When enabled, `/admin` requires HTTP Basic authentication
- `GET /admin/history` returns recent saved analyses
- `GET /admin/history/{id}` returns a specific saved analysis entry

History behavior:

- Analyses are saved when `PHISHSENSE_HISTORY_ENABLED=true`
- Default storage is SQLite at `PHISHSENSE_HISTORY_DB_PATH`

## Project Structure

- [Dockerfile](Dockerfile): Production-ready Python image for FastAPI app
- [docker-compose.yml](docker-compose.yml): One-command local container orchestration with persistent app data volume
- [.dockerignore](.dockerignore): Docker build context optimization and secret/runtime file exclusions
- [app/main.py](app/main.py): FastAPI app and `/analyze` endpoint
- [app/scoring_rules](app/scoring_rules): Modular scoring engine and rule configuration
- [app/ai_analysis.py](app/ai_analysis.py): AI explanation generation with safe fallbacks
- [app/settings.py](app/settings.py): Centralized environment/settings loader
- [app/logging_config.py](app/logging_config.py): Logging bootstrap
- [app/rate_limit.py](app/rate_limit.py): In-memory request throttling
- [app/security.py](app/security.py): Admin authentication dependency
- [app/history_store.py](app/history_store.py): SQLite analysis history persistence
- [app/templates/index.html](app/templates/index.html): Main web UI template for `/`
- [static/style.css](static/style.css): Responsive cross-device design system, severity indicator styling, and accessibility behavior
- [static/app.js](static/app.js): Frontend interactions, validation display, interactive indicator tabs, flag classification, and API rendering
- [tests](tests): Scoring, validation, and settings tests

## Render Deployment

- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Required env var: `GEMINI_API_KEY` (enables the primary Gemini-backed explanations)

## Student Project Notice

This project is for educational and portfolio purposes.

- It is not a production-grade security product.
- Results are advisory and may include false positives or false negatives.
- Always verify high-risk messages through official channels.

## Docs

- Full technical docs: [DEVELOPER_README.md](DEVELOPER_README.md)
- Project structure guide: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- Deployment notes: [DEPLOYMENT.md](DEPLOYMENT.md)

## CI

- GitHub Actions workflow: [.github/workflows/ci.yml](.github/workflows/ci.yml)
- Runs on push to `main` and all pull requests
- Executes Python tests and validates Docker Compose configuration

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).