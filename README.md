# 🏋️ Fitness Tracker Django API

A comprehensive fitness tracking web application with Django REST API backend and interactive frontend.

## 🚀 Features

- **User Management**: Registration, authentication, and profiles
- **Workout Tracking**: Log exercises, track calories, set goals
- **Performance Analytics**: Fitness index, progress tracking, analytics
- **Rankings & Leaderboards**: User rankings and achievements
- **Real-time Dashboard**: Interactive charts and metrics
- **API-First Design**: Complete REST API for all functionality

## 📋 Requirements

- Python 3.12+
- PostgreSQL (production)
- Node.js (for frontend development)

## 🛠️ Local Development Setup

### 1. Clone and Setup Environment

```bash
git clone <your-repo-url>
cd reza_deploy_work

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-super-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Development - SQLite)
# DATABASE_URL=sqlite:///./db.sqlite3

# Database (Production - PostgreSQL)
DATABASE_URL=postgresql://username:password@host:port/database_name

# Optional Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourapp.com

# Redis (Optional - for caching)
REDIS_URL=redis://localhost:6379/0
```

### 3. Database Setup

```bash
# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data (optional)
python manage.py loaddata fixtures/sample_data.json
```

### 4. Run Development Server

```bash
python manage.py runserver
```

Visit:
- **Main App**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **API Root**: http://127.0.0.1:8000/api/

## 🌐 Production Deployment

### Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/your-username/fitness-tracker)

1. **Fork this repository**
2. **Connect to Railway**:
   - Go to [Railway.app](https://railway.app)
   - Create new project from GitHub repo
   - Connect your forked repository

3. **Environment Variables**:
   ```env
   SECRET_KEY=your-production-secret-key
   DEBUG=False
   DATABASE_URL=postgresql://... (auto-provided by Railway)
   PRODUCTION_DOMAIN=your-app.railway.app
   ```

4. **Deploy**:
   - Railway will automatically build and deploy
   - Run migrations: `python manage.py migrate`
   - Create superuser: `python manage.py createsuperuser`

### Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

1. **Create Render Account**: Sign up at [render.com](https://render.com)

2. **Create PostgreSQL Database**:
   - Go to Dashboard > New > PostgreSQL
   - Note the connection details

3. **Create Web Service**:
   - Go to Dashboard > New > Web Service
   - Connect your GitHub repository
   - Configure:
     ```
     Build Command: pip install -r requirements.txt
     Start Command: gunicorn fitness_tracker.wsgi
     ```

4. **Environment Variables**:
   ```env
   SECRET_KEY=your-production-secret-key
   DEBUG=False
   DATABASE_URL=postgresql://... (from step 2)
   PRODUCTION_DOMAIN=your-app.onrender.com
   ```

5. **Deploy**:
   - Click "Create Web Service"
   - After deployment, run migrations via Render shell

### Deploy to Heroku

1. **Install Heroku CLI**
2. **Create Heroku App**:
   ```bash
   heroku create your-fitness-tracker-app
   heroku addons:create heroku-postgresql:hobby-dev
   ```

3. **Set Environment Variables**:
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set DEBUG=False
   heroku config:set PRODUCTION_DOMAIN=your-app.herokuapp.com
   ```

4. **Deploy**:
   ```bash
   git push heroku main
   heroku run python manage.py migrate
   heroku run python manage.py createsuperuser
   ```

## 🔧 Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `django-insecure-xyz...` |
| `DEBUG` | Debug mode | `False` (production) |
| `DATABASE_URL` | Database connection string | `postgresql://user:pass@host:port/db` |
| `PRODUCTION_DOMAIN` | Your app domain | `myapp.railway.app` |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `EMAIL_HOST` | SMTP server | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP port | `587` |
| `EMAIL_HOST_USER` | Email username | None |
| `EMAIL_HOST_PASSWORD` | Email password | None |
| `REDIS_URL` | Redis connection string | None |

## 📊 API Documentation

### Authentication Endpoints

```
POST /api/auth/register/     - Register new user
POST /api/auth/login/        - User login
POST /api/auth/logout/       - User logout
GET  /api/auth/profile/      - Get user profile
PUT  /api/auth/profile/      - Update user profile
```

### Workout Endpoints

```
GET  /api/workouts/sessions/     - List workout sessions
POST /api/workouts/sessions/     - Create workout session
GET  /api/workouts/exercises/    - List exercise types
GET  /api/workouts/goals/        - List workout goals
POST /api/workouts/goals/        - Create workout goal
```

### Performance Endpoints

```
GET  /api/performance/metrics/    - Get performance metrics
POST /api/performance/metrics/    - Update performance metrics
GET  /api/performance/summary/    - Get summary index
GET  /api/performance/goals/      - List fitness goals
POST /api/performance/goals/      - Create fitness goal
GET  /api/performance/analytics/  - Get workout analytics
```

### Ranking Endpoints

```
GET /api/rankings/user/          - Get user rankings
GET /api/rankings/leaderboard/   - Get leaderboard
GET /api/rankings/achievements/  - Get user achievements
```

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test fitness_app

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 📁 Project Structure

```
reza_deploy_work/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── runtime.txt              # Python version for deployment
├── Procfile                 # Process file for deployment
├── fitness_tracker/         # Django project settings
│   ├── __init__.py
│   ├── settings.py          # Project settings
│   ├── urls.py              # Main URL configuration
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
├── fitness_app/             # Main Django app
│   ├── models.py            # Database models
│   ├── views.py             # API views
│   ├── serializers.py       # DRF serializers
│   ├── urls.py              # App URL patterns
│   ├── admin.py             # Admin configuration
│   ├── apps.py              # App configuration
│   ├── tests.py             # Unit tests
│   └── migrations/          # Database migrations
├── templates/               # HTML templates
│   ├── index.html           # Main application page
│   └── login.html           # Login page
└── static/                  # Static files
    ├── js/                  # JavaScript files
    ├── css/                 # CSS files (extracted from HTML)
    └── data/                # Data files (CSV, etc.)
```

## 🔒 Security Features

- **Token Authentication**: Secure API access
- **CORS Protection**: Configurable cross-origin requests
- **SQL Injection Protection**: Django ORM safety
- **XSS Protection**: Template auto-escaping
- **CSRF Protection**: Cross-site request forgery prevention
- **HTTPS Enforcement**: Production SSL settings
- **Input Validation**: Comprehensive data validation

## 🚀 Performance Optimizations

- **Database Indexing**: Optimized queries
- **Static File Compression**: WhiteNoise integration
- **Caching**: Redis support for caching
- **Pagination**: API result pagination
- **Query Optimization**: Select/prefetch related objects

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**:
   - Check `DATABASE_URL` environment variable
   - Ensure PostgreSQL is running
   - Verify connection credentials

2. **Static Files Not Loading**:
   - Run `python manage.py collectstatic`
   - Check `STATIC_URL` and `STATIC_ROOT` settings
   - Verify `whitenoise` is in `MIDDLEWARE`

3. **CORS Issues**:
   - Check `CORS_ALLOWED_ORIGINS` in settings
   - Ensure `corsheaders` is in `INSTALLED_APPS`
   - Verify frontend domain is allowed

4. **Migration Errors**:
   - Run `python manage.py makemigrations`
   - Apply with `python manage.py migrate`
   - Check for conflicting migrations

### Debug Mode

For debugging in production (temporarily):

```bash
# Set debug mode (NOT recommended for production)
heroku config:set DEBUG=True  # Heroku
# Or set DEBUG=True in your deployment platform
```

## 📞 Support

- **Documentation**: [Project Wiki](link-to-wiki)
- **Issues**: [GitHub Issues](link-to-issues)
- **Email**: your-email@example.com

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 🎯 Roadmap

- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] Integration with fitness trackers
- [ ] Social features and challenges
- [ ] Machine learning recommendations
- [ ] Nutrition tracking
- [ ] Workout video integration

---

**Built with ❤️ using Django, DRF, and modern web technologies**
