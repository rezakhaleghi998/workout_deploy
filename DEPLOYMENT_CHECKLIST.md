# Deployment Checklist

## Pre-Deployment Checklist

### ✅ Files and Configuration
- [ ] `requirements.txt` contains all dependencies
- [ ] `Procfile` configured with correct web command
- [ ] `runtime.txt` specifies Python version
- [ ] `settings.py` uses environment variables
- [ ] Static files organized in `static/` directory
- [ ] Templates use Django static tags (`{% load static %}`)

### ✅ Environment Variables
Configure these in your hosting platform:

#### Required Variables
- [ ] `SECRET_KEY` - Django secret key (generate new one)
- [ ] `DEBUG` - Set to `False` for production
- [ ] `DATABASE_URL` - PostgreSQL connection string

#### Optional Variables
- [ ] `ALLOWED_HOSTS` - Your domain(s)
- [ ] `CORS_ALLOWED_ORIGINS` - Frontend domain(s)

### ✅ Security Settings
- [ ] `DEBUG = False` in production
- [ ] Strong `SECRET_KEY` generated
- [ ] `ALLOWED_HOSTS` configured
- [ ] CORS settings configured if needed

## Railway Deployment Steps

1. **Connect Repository**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login and deploy
   railway login
   railway init
   railway up
   ```

2. **Set Environment Variables**
   - Go to Railway dashboard
   - Navigate to your project
   - Set environment variables in Settings

3. **Database Setup**
   - Add PostgreSQL plugin in Railway
   - DATABASE_URL will be auto-configured

## Render Deployment Steps

1. **Create Web Service**
   - Connect GitHub repository
   - Select `reza_deploy_work` as root directory
   - Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - Start Command: `gunicorn fitness_tracker.wsgi:application`

2. **Environment Variables**
   - Set in Render dashboard under Environment tab

3. **Database Setup**
   - Create PostgreSQL database service
   - Use connection string as DATABASE_URL

## Heroku Deployment Steps

1. **Install Heroku CLI and Deploy**
   ```bash
   # Install Heroku CLI, then:
   heroku create your-app-name
   heroku addons:create heroku-postgresql:hobby-dev
   git push heroku main
   ```

2. **Configure Environment**
   ```bash
   heroku config:set SECRET_KEY="your-secret-key"
   heroku config:set DEBUG=False
   ```

## Post-Deployment Verification

### ✅ Test Endpoints
- [ ] Home page loads: `https://your-domain.com/`
- [ ] API root accessible: `https://your-domain.com/api/`
- [ ] Registration works: `POST /api/register/`
- [ ] Login works: `POST /api/login/`
- [ ] Static files load correctly

### ✅ Database Check
- [ ] Migrations applied successfully
- [ ] Admin interface accessible: `/admin/`
- [ ] Can create test user
- [ ] Can save workout sessions

### ✅ Performance Check
- [ ] Page load times acceptable
- [ ] API response times good
- [ ] No console errors in browser

## Troubleshooting

### Common Issues

1. **Static Files Not Loading**
   - Check `STATIC_URL` and `STATIC_ROOT` settings
   - Ensure `collectstatic` ran successfully
   - Verify WhiteNoise is installed

2. **Database Connection Errors**
   - Verify `DATABASE_URL` environment variable
   - Check database service is running
   - Ensure migrations are applied

3. **Application Errors**
   - Check application logs in hosting platform
   - Verify all environment variables are set
   - Ensure `DEBUG=False` in production

4. **CORS Issues (if using separate frontend)**
   - Configure `CORS_ALLOWED_ORIGINS`
   - Install `django-cors-headers`

### Useful Commands

```bash
# Check deployment logs
railway logs  # for Railway
heroku logs --tail  # for Heroku

# Run migrations manually
railway run python manage.py migrate  # for Railway
heroku run python manage.py migrate  # for Heroku

# Create superuser
railway run python manage.py createsuperuser  # for Railway
heroku run python manage.py createsuperuser  # for Heroku
```

## Support

If you encounter issues:
1. Check the logs first
2. Verify environment variables
3. Test locally with production settings
4. Check hosting platform documentation
5. Consult Django deployment guide

---

**Your Django Fitness Tracker is now ready for deployment! 🚀**
