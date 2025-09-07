# 🚂 Railway Environment Configuration Guide

## Copy these environment variables to your Railway dashboard:

### Required Environment Variables for Railway:

# Django Core Settings
SECRET_KEY=django-insecure-railway-change-this-50-character-secret-key-production
DEBUG=False
ALLOWED_HOSTS=*.railway.app,localhost,127.0.0.1

# Database (Auto-provided by Railway PostgreSQL plugin)
DATABASE_URL=${DATABASE_URL}

# Python Configuration
PYTHON_VERSION=3.12.0
PYTHONPATH=/app

# Django Admin Auto-Creation
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@workouttracker.com
DJANGO_SUPERUSER_PASSWORD=admin123

# Static Files Configuration
STATIC_URL=/static/
STATIC_ROOT=/app/staticfiles/

# Railway Service Configuration
RAILWAY_ENVIRONMENT_NAME=production
RAILWAY_SERVICE_NAME=workout-tracker

# Optional: Custom Domain
CUSTOM_DOMAIN=yourdomain.com

## How to Set Environment Variables in Railway:

1. Go to your Railway dashboard
2. Select your project
3. Click on "Variables" tab
4. Add each variable above (except DATABASE_URL - this is auto-provided)
5. Click "Deploy" to apply changes

## Railway PostgreSQL Setup:

1. In Railway dashboard, click "Add Service"
2. Select "PostgreSQL" 
3. Railway will automatically set DATABASE_URL
4. Your Django app will connect automatically

## Post-Deployment Access:

- Main App: https://workout-tracker.railway.app
- Admin Panel: https://workout-tracker.railway.app/admin/
- API Root: https://workout-tracker.railway.app/api/

Default Admin Login:
- Username: admin
- Password: admin123

## Railway CLI Commands (Optional):

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Deploy from local machine
railway up

# View logs
railway logs

# Open deployed app
railway open
```
