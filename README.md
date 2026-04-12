# PhishSense

PhishSense is a FastAPI web app that analyzes suspicious emails with configurable rule-based phishing detection and optional AI-generated explanations.

## What It Does

- Scores emails from 0 to 100 based on phishing indicators
- Labels risk as Low, Medium, or High
- Shows detected red flags
- Suggests a safe next action
- Generates a plain-English explanation with Gemini (when configured)
- Validates user input and returns field-level 422 errors for bad payloads

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

## Configuration

### Core Settings

- `GEMINI_API_KEY`: Gemini API key used for AI explanation generation
- `PHISHSENSE_GEMINI_MODEL`: Gemini model name (default: `gemini-2.5-flash`)
- `PHISHSENSE_LOG_LEVEL`: Backend logging level (default: `INFO`)
- `PHISHSENSE_APP_NAME`: FastAPI app title shown in OpenAPI docs

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
- `ai_explanation`
- `recommended_action`

Validation behavior:

- Invalid inputs return HTTP 422
- Response includes `detail` entries with field-specific error messages

## Project Structure

- [app/main.py](app/main.py): FastAPI app and `/analyze` endpoint
- [app/scoring_rules](app/scoring_rules): Modular scoring engine and rule configuration
- [app/ai_analysis.py](app/ai_analysis.py): AI explanation generation with safe fallbacks
- [app/settings.py](app/settings.py): Centralized environment/settings loader
- [app/logging_config.py](app/logging_config.py): Logging bootstrap
- [tests](tests): Scoring, validation, and settings tests

## Render Deployment

- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Required env var: `GEMINI_API_KEY` (if AI explanations are enabled)

## Student Project Notice

This project is for educational and portfolio purposes.

- It is not a production-grade security product.
- Results are advisory and may include false positives or false negatives.
- Always verify high-risk messages through official channels.

## Docs

- Full technical docs: [DEVELOPER_README.md](DEVELOPER_README.md)
- Deployment notes: [DEPLOYMENT.md](DEPLOYMENT.md)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).