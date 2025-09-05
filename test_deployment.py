#!/usr/bin/env python3
"""
Comprehensive deployment test script for Django fitness tracker app.
Tests all critical imports and configurations before deployment.
"""

import os
import sys
from pathlib import Path

def test_critical_imports():
    """Test all critical imports for deployment."""
    print("🔍 Testing critical imports...")
    
    try:
        import django
        print(f"✅ Django {django.get_version()} imported successfully")
    except ImportError as e:
        print(f"❌ Django import failed: {e}")
        return False
    
    try:
        import gunicorn
        print(f"✅ Gunicorn {gunicorn.__version__} imported successfully")
    except ImportError as e:
        print(f"❌ Gunicorn import failed: {e}")
        return False
    
    try:
        import dj_database_url
        print("✅ dj-database-url imported successfully")
    except ImportError as e:
        print(f"❌ dj-database-url import failed: {e}")
        return False
    
    try:
        import psycopg2
        print(f"✅ psycopg2 {psycopg2.__version__} imported successfully")
    except ImportError as e:
        print(f"❌ psycopg2 import failed: {e}")
        return False
    
    try:
        import whitenoise
        print("✅ whitenoise imported successfully")
    except ImportError as e:
        print(f"❌ whitenoise import failed: {e}")
        return False
    
    try:
        import rest_framework
        print("✅ Django REST Framework imported successfully")
    except ImportError as e:
        print(f"❌ Django REST Framework import failed: {e}")
        return False
    
    return True

def test_django_settings():
    """Test Django settings configuration."""
    print("\n🔍 Testing Django settings...")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_tracker.settings')
        import django
        django.setup()
        print("✅ Django settings loaded successfully")
        
        from django.conf import settings
        print(f"✅ DEBUG mode: {settings.DEBUG}")
        print(f"✅ ALLOWED_HOSTS configured: {len(settings.ALLOWED_HOSTS)} hosts")
        print(f"✅ Database engine: {settings.DATABASES['default']['ENGINE']}")
        
        return True
    except Exception as e:
        print(f"❌ Django settings failed: {e}")
        return False

def test_wsgi_application():
    """Test WSGI application import."""
    print("\n🔍 Testing WSGI application...")
    
    try:
        from fitness_tracker.wsgi import application
        print("✅ WSGI application imported successfully")
        print(f"✅ WSGI application type: {type(application)}")
        return True
    except Exception as e:
        print(f"❌ WSGI application import failed: {e}")
        return False

def test_database_connection():
    """Test database connection (if DATABASE_URL is set)."""
    print("\n🔍 Testing database connection...")
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("⚠️  DATABASE_URL not set - skipping database test")
        return True
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Run all deployment tests."""
    print("🚀 Starting Django Fitness Tracker Deployment Tests")
    print("=" * 60)
    
    # Set up environment
    BASE_DIR = Path(__file__).resolve().parent
    sys.path.insert(0, str(BASE_DIR))
    
    tests = [
        test_critical_imports,
        test_django_settings,
        test_wsgi_application,
        test_database_connection,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    if all(results):
        print("🎉 ALL TESTS PASSED! Deployment configuration is ready.")
        return 0
    else:
        print("❌ SOME TESTS FAILED! Fix the issues before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())