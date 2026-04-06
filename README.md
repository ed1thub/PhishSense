# PhishSense

PhishSense is an AI-assisted phishing email analysis web app built with **FastAPI**, **Gemini**, and **plain HTML/CSS/JavaScript**.

It combines a **rule-based phishing scoring engine** with an **AI explanation layer** to help users understand why an email may be suspicious.

## Features

- Analyze suspicious emails through a simple web interface
- Generate a phishing score from **0 to 100**
- Classify risk as **Low**, **Medium**, or **High**
- Detect common phishing indicators such as:
  - urgent pressure language
  - credential harvesting language
  - suspicious sender domains
  - shortened URLs
  - suspicious top-level domains
- Generate a plain-English explanation using Gemini
- Recommend a safe next action
- Includes sample phishing and safe email examples

## Tech Stack

- **Backend:** FastAPI
- **Frontend:** HTML, CSS, JavaScript
- **AI:** Gemini API
- **Testing:** Pytest

## Project Structure

```text
PhishSense/
├── app/
│   ├── ai_analysis.py
│   ├── main.py
│   ├── schemas.py
│   ├── scoring.py
│   ├── utils.py
│   └── templates/
│       └── index.html
├── static/
│   ├── app.js
│   └── style.css
├── tests/
│   └── test_scoring.py
├── .env
├── .gitignore
├── README.md
└── requirements.txt