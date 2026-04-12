# PhishSense

PhishSense is a student-built web app that analyzes suspicious emails using rule-based phishing detection plus AI-generated explanations.

## What It Does

- Scores emails from 0 to 100 based on phishing indicators
- Labels risk as Low, Medium, or High
- Shows detected red flags
- Suggests a safe next action
- Generates a plain-English explanation with Gemini

## Built With

- Python, FastAPI, Uvicorn
- HTML, CSS, JavaScript
- Google Gen AI SDK (Gemini)

## Quick Start

```bash
git clone https://github.com/<your-username>/PhishSense.git
cd PhishSense
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Optional phishing rule tuning:

- Set `PHISHSENSE_RULES_FILE` to a YAML file, or edit [app/scoring_rules/rules.yaml](app/scoring_rules/rules.yaml#L1)
- Override individual values with env vars like `PHISHSENSE_URGENT_PATTERNS`, `PHISHSENSE_SCORE_CAP`, or `PHISHSENSE_HIGH_RISK_THRESHOLD`

Run locally:

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

## Render Deployment

- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Required env var: `GEMINI_API_KEY`

## Student Project Notice

This project is for educational and portfolio purposes.

- It is not a production-grade security product.
- Results are advisory and may include false positives or false negatives.
- Always verify high-risk messages through official channels.

## Docs

- Full technical docs: `DEVELOPER_README.md`
- Deployment notes: `DEPLOYMENT.md`

## License

This project is licensed under the MIT License. See `LICENSE`.