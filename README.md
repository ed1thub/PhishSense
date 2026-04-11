# PhishSense

PhishSense is a phishing email analysis web app that combines rule-based threat detection with AI-generated explanations. It is designed to help users quickly assess suspicious emails by analyzing sender details, message content, embedded links, and common phishing indicators.

This project was built as a portfolio piece to demonstrate practical cybersecurity knowledge, backend API development, frontend integration, and applied AI usage in a real-world security context.

---

## Features

- Analyze suspicious email content for phishing indicators
- Detect common red flags such as:
  - urgent or threatening language
  - credential harvesting attempts
  - financial bait
  - mismatched sender and URL domains
  - suspicious top-level domains
  - shortened links
  - numeric or deceptive-looking domains
  - suspicious attachment wording
- Generate a phishing risk score
- Classify results into Low, Medium, or High risk
- Display rule-based findings clearly
- Generate AI-powered explanations using Gemini API
- Use sample phishing and legitimate email examples for quick testing

---

## Why I Built This

Phishing remains one of the most common and effective cyberattack methods. I built PhishSense to explore how a lightweight phishing triage tool could combine deterministic security rules with AI-generated explanation to help users understand *why* an email may be suspicious.

This project also gave me a chance to apply skills in:

- cybersecurity analysis
- Python backend development
- FastAPI REST API design
- JavaScript frontend development
- API integration
- UI/UX design for security tools

---

## Tech Stack

**Backend**
- Python
- FastAPI
- Uvicorn

**Frontend**
- HTML
- CSS
- JavaScript

**AI Integration**
- Google Gemini API

---

## How It Works

1. The user enters:
   - sender email
   - subject line
   - message body
   - embedded URL

2. The backend applies a set of phishing detection rules to identify suspicious patterns.

3. Each detected indicator contributes to a total phishing risk score.

4. The application classifies the email as:
   - **Low Risk**
   - **Medium Risk**
   - **High Risk**

5. Gemini generates a human-readable explanation summarizing why the email may be suspicious.

---

## Example Detection Indicators

PhishSense checks for patterns such as:

- pressure tactics like “urgent” or “immediately”
- requests to verify accounts or reset passwords
- suspicious payment or invoice language
- shortened URLs
- mismatched sender and destination domains
- suspicious TLDs
- domains containing misleading numbers
- suspicious wording related to attachments

---

## Project Structure

```bash
PhishSense/
│── backend/
│   ├── app.py
│   ├── detector.py
│   ├── ai_explainer.py
│   └── tests/
│
│── frontend/
│   ├── index.html
│   ├── styles.css
│   └── script.js
│
│── .env.example
│── requirements.txt
│── README.md
```
---

## Installation

1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/PhishSense.git
cd PhishSense
```
2. Create and activate a virtual environment
- Windows
```bash
python -m venv venv
venv\Scripts\activate
```
- macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
```
3. Install dependencies
```bash
pip install -r requirements.txt
```
4. Set up environment variables
```bash
GEMINI_API_KEY=your_api_key_here
```
---

## Running the Project

1. Start the backend
```bash
cd ~/PhishSense
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
2. The backend should now be available at:
```bash
http://127.0.0.1:8000
```