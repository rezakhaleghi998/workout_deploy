#!/usr/bin/env python3
"""
Pre-Deployment Verification Script
Checks if your Django project is ready for deployment
"""

import os
import sys
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a required file exists"""
    if os.path.exists(file_path):
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - FILE MISSING!")
        return False

def check_file_content(file_path, required_content, description):
    """Check if file contains required content"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            for item in required_content:
                if item not in content:
                    print(f"❌ {description} - Missing: {item}")
                    return False
        print(f"✅ {description}")
        return True
    except FileNotFoundError:
        print(f"❌ {description} - FILE NOT FOUND!")
        return False

def main():
    print("🔍 Pre-Deployment Verification")
    print("=" * 50)
    
    # Get current directory
    current_dir = Path.cwd()
    print(f"Checking directory: {current_dir}")
    print()
    
    results = []
    
    # Check essential files
    print("📁 Checking Essential Files:")
    essential_files = [
        ("manage.py", "Django management script"),
        ("requirements.txt", "Python dependencies"),
        ("Procfile", "Process configuration"),
        ("runtime.txt", "Python version specification"),
        ("fitness_tracker/settings.py", "Django settings"),
        ("fitness_tracker/urls.py", "Main URL configuration"),
        ("fitness_tracker/wsgi.py", "WSGI configuration"),
        ("fitness_app/models.py", "Database models"),
        ("fitness_app/views.py", "API views"),
        ("fitness_app/urls.py", "App URL configuration"),
    ]
    
    for file_path, description in essential_files:
        results.append(check_file_exists(file_path, description))
    
    print()
    
    # Check requirements.txt content
    print("📦 Checking Requirements:")
    required_packages = [
        "Django",
        "djangorestframework", 
        "django-cors-headers",
        "dj-database-url",
        "psycopg2-binary",
        "whitenoise",
        "gunicorn"
    ]
    results.append(check_file_content("requirements.txt", required_packages, "Required packages in requirements.txt"))
    
    print()
    
    # Check Procfile content
    print("⚙️  Checking Process Configuration:")
    procfile_content = ["web: gunicorn fitness_tracker.wsgi"]
    results.append(check_file_content("Procfile", procfile_content, "Procfile web command"))
    
    print()
    
    # Check settings.py for production readiness
    print("🔧 Checking Django Settings:")
    settings_requirements = [
        "dj_database_url",
        "ALLOWED_HOSTS",
        "whitenoise",
        "STATIC_ROOT",
        "SECRET_KEY"
    ]
    results.append(check_file_content("fitness_tracker/settings.py", settings_requirements, "Production settings configuration"))
    
    print()
    
    # Check template files
    print("🎨 Checking Templates:")
    template_files = [
        ("templates/index.html", "Main template"),
        ("templates/login.html", "Login template"),
    ]
    
    for file_path, description in template_files:
        results.append(check_file_exists(file_path, description))
    
    print()
    
    # Check static files directory
    print("📁 Checking Static Files:")
    static_dirs = [
        ("static/", "Static files directory"),
        ("static/js/", "JavaScript files directory"),
    ]
    
    for dir_path, description in static_dirs:
        results.append(check_file_exists(dir_path, description))
    
    print()
    
    # Environment check
    print("🌍 Environment Check:")
    try:
        import django
        print(f"✅ Django version: {django.get_version()}")
        results.append(True)
    except ImportError:
        print("❌ Django not installed!")
        results.append(False)
    
    try:
        import rest_framework
        print("✅ Django REST Framework installed")
        results.append(True)
    except ImportError:
        print("❌ Django REST Framework not installed!")
        results.append(False)
    
    print()
    
    # Security check
    print("🔒 Security Check:")
    
    # Check if DEBUG is properly configured
    settings_file = "fitness_tracker/settings.py"
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            content = f.read()
            if "DEBUG = os.environ.get('DEBUG'" in content:
                print("✅ DEBUG setting uses environment variable")
                results.append(True)
            else:
                print("❌ DEBUG setting should use environment variable")
                results.append(False)
            
            if "SECRET_KEY = os.environ.get('SECRET_KEY'" in content:
                print("✅ SECRET_KEY uses environment variable")
                results.append(True)
            else:
                print("❌ SECRET_KEY should use environment variable")
                results.append(False)
    
    print()
    print("=" * 50)
    print("📊 Verification Results")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Checks Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL CHECKS PASSED! Ready for deployment!")
        print()
        print("Next steps:")
        print("1. Push your code to GitHub")
        print("2. Follow the deployment guide for Railway or Render")
        print("3. Set environment variables on your hosting platform")
        print("4. Run deployment test after deployment")
        return True
    else:
        print("⚠️  Some checks failed. Fix the issues above before deploying.")
        print()
        print("Common fixes:")
        print("- Install missing packages: pip install -r requirements.txt")
        print("- Create missing files using the deployment guide")
        print("- Check file paths and content")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
