# PhishSense Deployment Guide

## Deploy to Render.com (Free)

### Step 1: Push to GitHub
If you haven't already, commit and push your code to GitHub:
```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### Step 2: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click **"New"** → **"Web Service"**
4. Select your `PhishSense` repository
5. Configure:
   - **Name**: `phishsense` (or your choice)
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
   - **Plan**: Free (blue pill)

### Step 3: Add Environment Variables
1. Scroll down to **Environment** section
2. Add this variable:
   - **Key**: `GEMINI_API_KEY`
   - **Value**: [Your Gemini API key](https://aistudio.google.com/app/apikey)
3. Click **"Create Web Service"**

### Step 4: Wait for Deployment
The app will build and deploy automatically. Once done, you'll get a public URL like:
```
https://phishsense-xxxxx.onrender.com
```

Share this link with your friends!

---

## Alternative: Deploy to Replit (Even Easier)
If you want the quickest option:
1. Go to [replit.com](https://replit.com)
2. Click **"Import from Github"** and select your repo
3. Add `GEMINI_API_KEY` to the **Secrets** panel
4. Click **"Run"**
5. Get a shareable link

---

## Notes
- Render free tier auto-sleeps after 15 min inactivity (wakes on request)
- Render allows free deployments with 0.5 CPU / 512MB RAM
- Each friend can use your API key (add rate limiting if needed)
- To use a production API key, consider upgrading later

---

## .gitignore Check
Make sure `.env` is in `.gitignore` so your API key doesn't leak:
```
.env
.venv
__pycache__
```
