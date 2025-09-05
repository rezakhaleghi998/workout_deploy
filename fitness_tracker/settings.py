"""
Django settings for fitness_tracker project.
EMERGENCY DEPLOYMENT CONFIGURATION - BULLETPROOF SETUP
"""

import os
import sys
from pathlib import Path

# ============================================
# BASE CONFIGURATION
# ============================================

BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================
# SECURITY SETTINGS - PRODUCTION READY
# ============================================

SECRET_KEY = os.environ.get(
    'SECRET_KEY', 
    'django-insecure-emergency-key-change-in-production-immediately'
)

DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# ALLOWED HOSTS - Comprehensive for Render
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    '.render.com',
    '.onrender.com',
    'workout-deploy.onrender.com',
]

# Add custom domain if provided
CUSTOM_DOMAIN = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if CUSTOM_DOMAIN:
    ALLOWED_HOSTS.append(CUSTOM_DOMAIN)

# Allow all hosts for emergency deployment
if os.environ.get('EMERGENCY_ALLOW_ALL_HOSTS', 'False').lower() == 'true':
    ALLOWED_HOSTS = ['*']

# ============================================
# DJANGO APPLICATIONS - BULLETPROOF CONFIG
# ============================================

# Core Django apps - NEVER CHANGE
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# Third-party apps - Safe imports only
THIRD_PARTY_APPS = []

# Add DRF only if available
try:
    import rest_framework
    THIRD_PARTY_APPS.append('rest_framework')
    THIRD_PARTY_APPS.append('rest_framework.authtoken')
except ImportError:
    print("WARNING: djangorestframework not available")

# Add CORS only if available
try:
    import corsheaders
    THIRD_PARTY_APPS.append('corsheaders')
except ImportError:
    print("WARNING: django-cors-headers not available")

# Local apps - Safe configuration
LOCAL_APPS = [
    'fitness_app.apps.FitnessAppConfig',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ============================================
# MIDDLEWARE - BULLETPROOF CONFIGURATION
# ============================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
]

# Add WhiteNoise if available
try:
    import whitenoise
    MIDDLEWARE.append('whitenoise.middleware.WhiteNoiseMiddleware')
except ImportError:
    print("WARNING: whitenoise not available")

# Add CORS middleware if available
try:
    import corsheaders
    MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware')
except ImportError:
    pass

# Core middleware - ALWAYS REQUIRED
MIDDLEWARE.extend([
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
])

# ============================================
# URL AND TEMPLATES CONFIGURATION
# ============================================

ROOT_URLCONF = 'fitness_tracker.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'fitness_tracker.wsgi.application'

# ============================================
# DATABASE CONFIGURATION - BULLETPROOF
# ============================================

DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Production database configuration
    try:
        import dj_database_url
        DATABASES = {
            'default': dj_database_url.parse(
                DATABASE_URL, 
                conn_max_age=600,
                conn_health_checks=True,
            )
        }
    except ImportError:
        # Fallback manual parsing
        import urllib.parse as urlparse
        url = urlparse.urlparse(DATABASE_URL)
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': url.path[1:],
                'USER': url.username,
                'PASSWORD': url.password,
                'HOST': url.hostname,
                'PORT': url.port or 5432,
                'OPTIONS': {
                    'conn_max_age': 600,
                    'sslmode': 'require',
                },
            }
        }
else:
    # Development/fallback database
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ============================================
# AUTHENTICATION CONFIGURATION
# ============================================

AUTH_USER_MODEL = 'fitness_app.User'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ============================================
# REST FRAMEWORK CONFIGURATION - SAFE
# ============================================

try:
    import rest_framework
    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'rest_framework.authentication.TokenAuthentication',
        ],
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
        ],
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': 50,
        'DEFAULT_RENDERER_CLASSES': [
            'rest_framework.renderers.JSONRenderer',
        ],
        'DEFAULT_PARSER_CLASSES': [
            'rest_framework.parsers.JSONParser',
            'rest_framework.parsers.FormParser',
            'rest_framework.parsers.MultiPartParser',
        ],
    }
except ImportError:
    pass

# ============================================
# CORS CONFIGURATION - SAFE
# ============================================

try:
    import corsheaders
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    
    # Add production domain
    if CUSTOM_DOMAIN:
        CORS_ALLOWED_ORIGINS.extend([
            f"https://{CUSTOM_DOMAIN}",
            f"http://{CUSTOM_DOMAIN}",
        ])
    
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_HEADERS = [
        'accept',
        'accept-encoding',
        'authorization',
        'content-type',
        'dnt',
        'origin',
        'user-agent',
        'x-csrftoken',
        'x-requested-with',
    ]
except ImportError:
    pass

# ============================================
# INTERNATIONALIZATION
# ============================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ============================================
# STATIC FILES - BULLETPROOF CONFIGURATION
# ============================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
] if (BASE_DIR / 'static').exists() else []

# Configure WhiteNoise if available
try:
    import whitenoise
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    WHITENOISE_USE_FINDERS = True
    WHITENOISE_AUTOREFRESH = DEBUG
except ImportError:
    pass

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ============================================
# DEFAULT PRIMARY KEY
# ============================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================
# LOGGING CONFIGURATION - PRODUCTION READY
# ============================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose' if DEBUG else 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG' if DEBUG else 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'fitness_app': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

# ============================================
# EMERGENCY DEPLOYMENT SETTINGS
# ============================================

# Disable problematic features for deployment
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = None
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Cache configuration - Simple for deployment
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

print(f"🔧 Django settings loaded successfully")
print(f"🔧 DEBUG mode: {DEBUG}")
print(f"🔧 Database: {'PostgreSQL' if DATABASE_URL else 'SQLite'}")
print(f"🔧 Installed apps: {len(INSTALLED_APPS)} apps")