# 🚨 CLAUDE AI DEPLOYMENT FIX PROMPT - RENDER DEPLOYMENT FAILED

## URGENT: DEPLOYMENT FAILED - NEED IMMEDIATE FIX

```
My Django fitness tracker app deployment on Render is failing with status 127. I can see the error logs and need immediate help to fix this.

CURRENT SITUATION:
- App is deployed on Render at: workout_deploy
- GitHub repo: https://github.com/rezakhaleghi998/workout_deploy.git
- Branch: main
- Deployment status: FAILED (Status 127)

ERROR LOGS FROM RENDER:
- ImportError: Couldn't import Django
- gunicorn: command not found
- Build completed successfully but app won't start
- Exited with status 127

VISIBLE ISSUES IN LOGS:
1. "ImportError: Couldn't import Django. Are you sure it's installed and available on your PYTHONPATH environment variable? Did you forget to activate a virtual environment?"
2. "bash: line 1: gunicorn: command not found"
3. Build shows "Build completed successfully!" but deploy fails
4. Shows "Uploading build..." then "Deployed" but app exits immediately

APP REQUIREMENTS (MUST WORK EXACTLY AS LOCAL):
✅ Django 4.2.7 fitness tracker
✅ Real-time calorie calculations
✅ User authentication system
✅ Dynamic UI interactions
✅ Profile modals functionality
✅ API endpoints working
✅ Static files serving correctly

CURRENT DEPLOYMENT FILES:
- requirements.txt: Django==4.2.7, djangorestframework, gunicorn, etc.
- Procfile: web: gunicorn fitness_tracker.wsgi:application
- build.sh: pip install, collectstatic, migrate commands
- runtime.txt: python-3.12.0
- settings.py: Production ready with DATABASE_URL

IMMEDIATE HELP NEEDED:
1. Diagnose why Django import is failing despite successful build
2. Fix gunicorn command not found error
3. Resolve PYTHONPATH/virtual environment issues
4. Ensure proper Python environment setup on Render
5. Fix any missing dependencies or configuration issues
6. Get the app running successfully on Render

CRITICAL CONSTRAINTS:
- App MUST work exactly like localhost:8000
- NO functionality changes allowed
- All features must be preserved
- Authentication, calculations, and UI must work identically

RENDER CONFIGURATION:
- Runtime: Python 3
- Build Command: ./build.sh
- Start Command: gunicorn fitness_tracker.wsgi:application
- Environment variables: SECRET_KEY, DATABASE_URL (PostgreSQL)

Please provide immediate step-by-step troubleshooting to:
1. Fix the Django import error
2. Resolve gunicorn command issues
3. Ensure proper Python environment
4. Get the app successfully deployed and running
5. Verify all functionality works post-deployment

This is urgent - I need the app deployed and working with zero functionality changes.
```

## HOW TO USE THIS PROMPT:

1. **Copy the entire prompt above** (from "My Django fitness tracker..." to "...zero functionality changes.")
2. **Paste it into Claude Code AI**
3. **Follow Claude's immediate troubleshooting steps**
4. **Implement fixes in your Render dashboard**

## EXPECTED FIXES CLAUDE WILL PROVIDE:

- Fix Django import path issues
- Resolve gunicorn installation problems
- Configure proper Python environment
- Fix PYTHONPATH settings
- Ensure all dependencies are correctly installed
- Verify Render configuration settings

## URGENCY LEVEL: HIGH
Your app needs immediate deployment fixes to work on Render.
