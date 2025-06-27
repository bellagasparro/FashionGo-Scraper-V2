# Email Scraper Deployment Guide

## Option 1: Railway (Recommended - Free & Easy)

1. Go to [Railway.app](https://railway.app)
2. Sign up with GitHub (or create account)
3. Click "New Project" → "Deploy from GitHub repo"
4. Upload/connect your project files
5. Railway will automatically detect Python and deploy
6. You'll get a permanent URL like: `https://your-app-name.railway.app`

**Files needed for Railway:**
- All your current files
- `Procfile` ✅ (created)
- `requirements.txt` ✅ (created)
- `railway.json` ✅ (created)
- `runtime.txt` ✅ (created)

## Option 2: Render (Free Tier Available)

1. Go to [Render.com](https://render.com)
2. Sign up and create new "Web Service"
3. Connect GitHub or upload files
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `python3 email_scraper_app.py`

## Option 3: Heroku (Has Free Tier)

1. Install Heroku CLI
2. Run these commands:
```bash
heroku create your-app-name
git add .
git commit -m "Deploy email scraper"
git push heroku main
```

## Option 4: PythonAnywhere (Free Tier)

1. Sign up at [PythonAnywhere.com](https://pythonanywhere.com)
2. Upload your files
3. Create a new web app
4. Configure WSGI file to point to your Flask app

## Quick Deploy Files

All necessary deployment files have been created:

- ✅ `email_scraper_app.py` - Main Flask application
- ✅ `templates/index.html` - Web interface
- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - Process configuration
- ✅ `railway.json` - Railway specific config
- ✅ `runtime.txt` - Python version specification

## What You Get

Once deployed, you'll have:
- 24/7 availability (no need for your computer to be on)
- Permanent public URL
- Automatic scaling
- SSL certificate (https://)
- No ngrok dependency

## Recommended Next Steps

1. **Railway** is the easiest - just drag and drop your files
2. The app will be available at a permanent URL
3. Share the URL with anyone who needs to use the email scraper
4. The service will handle all the infrastructure automatically 