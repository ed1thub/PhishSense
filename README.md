# PhishSense

PhishSense is a FastAPI-powered phishing email analyzer that combines rule-based scoring with AI-generated explanations.

Paste an email sender, subject, body, and optional URL, then PhishSense returns:

- a phishing score out of 100
- a risk label (Low, Medium, High)
- detected red flags
- a recommended action
- an AI explanation powered by Gemini

## Features

- Rule-based phishing detection engine
- AI explanation generation using Google Gemini (gemini-2.5-flash)
- Clear risk visualization in a modern web UI
- Built-in sample phishing and safe email examples
- JSON API endpoint for programmatic use

## Detection Signals

PhishSense currently checks for:

- urgent pressure language
- credential-harvesting terms
- financial bait language
- sender domain with numeric lookalike patterns
- URL shortener usage
- sender and URL domain mismatch
- suspicious TLDs (.ru, .xyz, .top, .click, .shop)
- excessive punctuation
- suspicious attachment/download wording

## Tech Stack

- Python
- FastAPI + Uvicorn
- Jinja2 templates + static HTML/CSS/JavaScript frontend
- python-dotenv for environment variables
- Google Gen AI SDK (google-genai)
- Pytest for tests

## Project Structure

```text
PhishSense/
├── app/
│   ├── ai_analysis.py
│   ├── main.py
│   ├── schemas.py
│   ├── scoring.py
│   └── templates/
│       └── index.html
├── static/
│   ├── app.js
│   └── style.css
├── tests/
│   └── test_scoring.py
├── requirements.txt
└── README.md
```

## Getting Started (Local)

### 1. Clone

```bash
git clone https://github.com/<your-username>/PhishSense.git
cd PhishSense
```

### 2. Create and activate a virtual environment

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

If `GEMINI_API_KEY` is missing, rule-based analysis still works and the app will return a fallback AI message.

### 5. Run the app

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## API

### Endpoint

`POST /analyze`

### Request body

```json
{
   "sender": "support@micros0ft-login.com",
   "subject": "Urgent: Verify your account now",
   "body": "Your account has been suspended...",
   "url": "https://bit.ly/security-check"
}
```

### Response body

```json
{
   "score": 80,
   "risk_level": "High",
   "red_flags": [
      "Urgent pressure language detected",
      "Credential or account verification language detected"
   ],
   "ai_explanation": "This email appears suspicious because...",
   "recommended_action": "Do not click links or reply. Verify the message through the sender's official website or support channel."
}
```

## Run Tests

```bash
PYTHONPATH=. pytest -q
```

## Deploy on Render

Use a Render Web Service with these settings:

- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Add environment variable in Render:

- `GEMINI_API_KEY=<your_key>`

After deploy:

- test home page load
- run one `/analyze` request from the UI
- confirm no 500 errors in logs

## Notes

- The UI escapes API output before rendering to reduce XSS risk.
- Gemini import is lazy-loaded to avoid startup crashes if the AI SDK has runtime issues.

## License

Add your preferred license (MIT, Apache-2.0, etc.) in this repository.