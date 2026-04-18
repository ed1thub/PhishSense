# PhishSense Project Structure

This document describes the current repository layout, responsibility boundaries, and safe extension points.

## Top-Level Layout

- `app/`: backend application package (API, analysis, scoring, config)
- `static/`: frontend assets served by FastAPI
- `tests/`: automated tests for scoring, validation, and settings
- `Dockerfile`: container image definition for running the app
- `docker-compose.yml`: local orchestration with volume-backed persistence
- `.dockerignore`: Docker build context filtering
- `README.md`: user-facing setup and usage
- `DEVELOPER_README.md`: implementation notes and workflow details
- `DEPLOYMENT.md`, `render.yaml`, `Procfile`: deployment configuration and notes

## Backend Layout (`app/`)

- `main.py`: FastAPI app creation, routes, template/static setup, API response handling
- `schemas.py`: request and response models with input validation rules
- `ai_analysis.py`: Gemini explanation generation with safe fallback handling for transient API failures
- `settings.py`: centralized environment-backed settings loader
- `logging_config.py`: logging bootstrap and formatting
- `rate_limit.py`: in-memory rate limiter utility
- `security.py`: HTTP Basic auth dependency for admin routes
- `history_store.py`: SQLite persistence for saved analysis history
- `templates/index.html`: UI template rendered for `/`

### Scoring Subsystem (`app/scoring_rules/`)

- `__init__.py`: public entrypoint export for scoring
- `engine.py`: orchestration of rule modules into one `analyze_email` result
- `config.py`: YAML and environment config loader for scoring rules
- `rules.yaml`: default rule definitions and thresholds
- `content.py`: body/subject language signal scoring
- `domain.py`: sender and URL/domain signal scoring
- `policy.py`: score caps, thresholds, and risk-action mapping
- `common.py`: shared helpers (pattern matching, domain extraction)

## Frontend Layout (`static/`)

- `app.js`: form submission flow, sample loading, API handling, result rendering, validation error mapping, and flag severity classification
- `style.css`: modern responsive design system (layout, typography, cards, forms, severity indicator states, motion, and reduced-motion support)

## UI Rendering Flow

1. `GET /` renders `app/templates/index.html`.
2. The template loads `static/style.css` and `static/app.js`.
3. Frontend JS submits payloads to `POST /analyze` and updates the results panel in-place.
4. Results rendering emphasizes flagged indicators with severity summary tabs and per-flag severity labels.
5. Indicator details remain hidden until the corresponding severity tab is selected.
6. CSS breakpoints adapt the two-column desktop layout to a stacked mobile layout with touch and safe-area optimization.

## Tests (`tests/`)

- `conftest.py`: global test fixtures (Gemini mock, limiter/history reset)
- `test_scoring.py`: baseline scoring behavior
- `test_scoring_extended.py`: scenario-heavy scoring tests
- `test_rule_config.py`: rule config precedence and override behavior
- `test_validation_and_ai.py`: payload validation and AI error safety
- `test_api_integration.py`: endpoint integration coverage (validation, auth, history)
- `test_settings.py`: settings defaults and environment override behavior

## Request Flow

1. Browser sends payload to `POST /analyze`.
2. `schemas.EmailInput` validates and normalizes input.
3. `scoring_rules.engine.analyze_email` prepares deterministic fallback values.
4. `ai_analysis.generate_ai_assessment` asks Gemini for score, risk level, red flags, recommendation, and explanation.
5. If Gemini is unavailable or returns an invalid payload, fallback values are used.
6. Result is optionally persisted to SQLite history storage.
7. Endpoint returns normalized `AnalysisResult` response including explainability rule hits.

## Configuration Flow

- Runtime settings are resolved by `app/settings.py`.
- Logging is initialized from `PHISHSENSE_LOG_LEVEL`.
- Scoring rules load from `app/scoring_rules/rules.yaml` by default.
- `PHISHSENSE_RULES_FILE` and rule-specific env vars override defaults.
- Rate limiting and admin mode are controlled through `PHISHSENSE_RATE_LIMIT_*` and `PHISHSENSE_ADMIN_*`.
- History persistence is controlled through `PHISHSENSE_HISTORY_*`.
- Gemini-backed explanations are the primary design point; the app returns a local fallback explanation when Gemini is unavailable or returns a transient failure.

## Professional Structure Guidelines

- Keep business logic in `app/scoring_rules/`, not in route handlers.
- Keep environment access centralized in `app/settings.py`.
- Add new rules in focused modules (`content.py` or `domain.py`) before touching orchestration.
- Prefer adding tests in `tests/` whenever behavior changes.
- Avoid adding utility files unless they have clear, shared responsibility.
