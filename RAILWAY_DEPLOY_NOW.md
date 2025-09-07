# 🚂 Railway Deployment - Quick Guide

## Ready to Deploy!

Your Django workout app is now configured for Railway deployment.

## 🚀 Deploy Steps

### 1. Go to Railway
Visit: https://railway.app

### 2. Connect GitHub
- Click "Deploy from GitHub repo"
- Select: `rezakhaleghi998/workout_deploy`

### 3. Add PostgreSQL Database
- In Railway dashboard, click "Add Service"
- Select "PostgreSQL"
- Railway will automatically set `DATABASE_URL`

### 4. Set Environment Variables (Optional)
Only set these if you want custom values:
```
SECRET_KEY=your-secret-key-here
DEBUG=False
```

### 5. Deploy!
Railway will automatically:
- ✅ Install dependencies from `requirements.txt`
- ✅ Run database migrations
- ✅ Collect static files
- ✅ Start your app with Gunicorn

## 🔗 Access Your App

After deployment:
- **Main App**: `https://your-app-name.railway.app`
- **Admin Panel**: `https://your-app-name.railway.app/admin/`

## 🔑 Admin Access

Create admin user in Railway terminal:
```bash
python manage.py shell
from django.contrib.auth.models import User
User.objects.create_superuser('admin', 'admin@example.com', 'your_password')
```

## ✅ What's Already Configured

- ✅ `railway.json` - Railway deployment config
- ✅ `nixpacks.toml` - Build configuration
- ✅ PostgreSQL database support
- ✅ Static files with WhiteNoise
- ✅ Production-ready settings
- ✅ Automatic migrations

Your app should deploy successfully on Railway now!
