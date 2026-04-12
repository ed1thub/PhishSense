# PhishSense Project Structure

This document describes the current repository layout, responsibility boundaries, and safe extension points.

## Top-Level Layout

- `app/`: backend application package (API, analysis, scoring, config)
- `static/`: frontend assets served by FastAPI
- `tests/`: automated tests for scoring, validation, and settings
- `README.md`: user-facing setup and usage
- `DEVELOPER_README.md`: implementation notes and workflow details
- `DEPLOYMENT.md`, `render.yaml`, `Procfile`: deployment configuration and notes

## Backend Layout (`app/`)

- `main.py`: FastAPI app creation, routes, template/static setup, API response handling
- `schemas.py`: request and response models with input validation rules
- `ai_analysis.py`: Gemini explanation generation with safe fallback handling
- `settings.py`: centralized environment-backed settings loader
- `logging_config.py`: logging bootstrap and formatting
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

- `app.js`: form submission flow, API handling, result rendering, validation error mapping
- `style.css`: page styling and validation/error state styles

## Tests (`tests/`)

- `test_scoring.py`: baseline scoring behavior
- `test_rule_config.py`: rule config precedence and override behavior
- `test_validation_and_ai.py`: payload validation and AI error safety
- `test_settings.py`: settings defaults and environment override behavior

## Request Flow

1. Browser sends payload to `POST /analyze`.
2. `schemas.EmailInput` validates and normalizes input.
3. `scoring_rules.engine.analyze_email` calculates score, risk level, red flags, and recommendation.
4. `ai_analysis.generate_ai_explanation` attempts AI explanation generation.
5. Endpoint returns normalized `AnalysisResult` response.

## Configuration Flow

- Runtime settings are resolved by `app/settings.py`.
- Logging is initialized from `PHISHSENSE_LOG_LEVEL`.
- Scoring rules load from `app/scoring_rules/rules.yaml` by default.
- `PHISHSENSE_RULES_FILE` and rule-specific env vars override defaults.

## Professional Structure Guidelines

- Keep business logic in `app/scoring_rules/`, not in route handlers.
- Keep environment access centralized in `app/settings.py`.
- Add new rules in focused modules (`content.py` or `domain.py`) before touching orchestration.
- Prefer adding tests in `tests/` whenever behavior changes.
- Avoid adding utility files unless they have clear, shared responsibility.
