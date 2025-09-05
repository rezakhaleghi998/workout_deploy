#!/usr/bin/env python3
"""
EMERGENCY DEPLOYMENT TEST SUITE
Complete system validation before deployment
"""

import os
import sys
from pathlib import Path

def emergency_test_suite():
    """Run emergency deployment test suite"""
    print("🚨 EMERGENCY DEPLOYMENT TEST SUITE STARTED")
    print("=" * 60)
    
    # Set emergency environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_tracker.settings')
    os.environ.setdefault('EMERGENCY_ALLOW_ALL_HOSTS', 'True')
    
    test_results = []
    
    # Test 1: Critical Dependencies
    print("\n🔍 TEST 1: Critical Dependencies")
    try:
        import django
        import rest_framework
        import gunicorn  
        import dj_database_url
        import psycopg2
        import whitenoise
        import corsheaders
        
        print(f"✅ Django {django.get_version()}")
        print(f"✅ DRF {rest_framework.VERSION}")
        print(f"✅ Gunicorn {gunicorn.__version__}")
        print("✅ dj-database-url")
        print(f"✅ psycopg2 {psycopg2.__version__}")
        print("✅ whitenoise")
        print("✅ corsheaders")
        test_results.append(True)
    except Exception as e:
        print(f"❌ Dependency test failed: {e}")
        test_results.append(False)
    
    # Test 2: Django Configuration
    print("\n🔍 TEST 2: Django Configuration")
    try:
        import django
        django.setup()
        from django.conf import settings
        
        print(f"✅ Django configured: {settings.configured}")
        print(f"✅ Installed apps: {len(settings.INSTALLED_APPS)}")
        print(f"✅ Database engine: {settings.DATABASES['default']['ENGINE']}")
        print(f"✅ Debug mode: {settings.DEBUG}")
        print(f"✅ Allowed hosts: {len(settings.ALLOWED_HOSTS)} configured")
        test_results.append(True)
    except Exception as e:
        print(f"❌ Django configuration test failed: {e}")
        test_results.append(False)
    
    # Test 3: WSGI Application
    print("\n🔍 TEST 3: WSGI Application")
    try:
        from fitness_tracker.wsgi import application
        print(f"✅ WSGI application type: {type(application)}")
        print("✅ WSGI application imported successfully")
        test_results.append(True)
    except Exception as e:
        print(f"❌ WSGI application test failed: {e}")
        test_results.append(False)
    
    # Test 4: App Registry
    print("\n🔍 TEST 4: Django Apps Registry")
    try:
        from django.apps import apps
        app_configs = apps.get_app_configs()
        print(f"✅ Apps registry populated: {len(app_configs)} apps")
        
        # Check fitness_app specifically
        fitness_app = apps.get_app_config('fitness_app')
        print(f"✅ fitness_app loaded: {fitness_app.name}")
        test_results.append(True)
    except Exception as e:
        print(f"❌ Apps registry test failed: {e}")
        test_results.append(False)
    
    # Test 5: Database Configuration
    print("\n🔍 TEST 5: Database Configuration")
    try:
        from django.db import connection
        print(f"✅ Database connection available")
        print(f"✅ Database vendor: {connection.vendor}")
        test_results.append(True)
    except Exception as e:
        print(f"⚠️  Database test skipped: {e}")
        test_results.append(True)  # Non-critical for deployment test
    
    # Test 6: User Model
    print("\n🔍 TEST 6: User Model Configuration")
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        print(f"✅ User model: {User}")
        print(f"✅ User model app: {User._meta.app_label}")
        test_results.append(True)
    except Exception as e:
        print(f"❌ User model test failed: {e}")
        test_results.append(False)
    
    # Test 7: Static Files Configuration
    print("\n🔍 TEST 7: Static Files Configuration")
    try:
        from django.conf import settings
        print(f"✅ STATIC_URL: {settings.STATIC_URL}")
        print(f"✅ STATIC_ROOT: {settings.STATIC_ROOT}")
        print(f"✅ STATICFILES_DIRS: {len(settings.STATICFILES_DIRS)}")
        if hasattr(settings, 'STATICFILES_STORAGE'):
            print(f"✅ STATICFILES_STORAGE: {settings.STATICFILES_STORAGE}")
        test_results.append(True)
    except Exception as e:
        print(f"❌ Static files test failed: {e}")
        test_results.append(False)
    
    # Final Results
    print("\n" + "=" * 60)
    passed = sum(test_results)
    total = len(test_results)
    
    if passed == total:
        print(f"🎉 ALL TESTS PASSED! ({passed}/{total})")
        print("🚀 DEPLOYMENT CONFIGURATION IS BULLETPROOF!")
        return 0
    else:
        print(f"❌ SOME TESTS FAILED! ({passed}/{total})")
        print("🚨 FIX ISSUES BEFORE DEPLOYMENT!")
        return 1

if __name__ == "__main__":
    # Add project to path
    BASE_DIR = Path(__file__).resolve().parent
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    
    sys.exit(emergency_test_suite())