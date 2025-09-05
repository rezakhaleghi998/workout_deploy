"""
WSGI config for fitness_tracker project.
EMERGENCY DEPLOYMENT CONFIGURATION - BULLETPROOF SETUP

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

# ============================================
# EMERGENCY WSGI CONFIGURATION
# ============================================

# Ensure project is in Python path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_tracker.settings')

try:
    from django.core.wsgi import get_wsgi_application
    print("🔧 WSGI: Django core imported successfully")
except ImportError as e:
    print(f"❌ WSGI: Failed to import Django core: {e}")
    print(f"🔧 WSGI: Python path: {sys.path}")
    print(f"🔧 WSGI: Current directory: {os.getcwd()}")
    raise

try:
    application = get_wsgi_application()
    print("🔧 WSGI: Application created successfully")
except Exception as e:
    print(f"❌ WSGI: Failed to create application: {e}")
    print(f"🔧 WSGI: Settings module: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    
    # Emergency debugging
    try:
        import django
        from django.conf import settings
        print(f"🔧 WSGI: Django version: {django.get_version()}")
        print(f"🔧 WSGI: Settings configured: {settings.configured}")
        print(f"🔧 WSGI: Installed apps: {len(settings.INSTALLED_APPS) if settings.configured else 'Not configured'}")
    except Exception as debug_e:
        print(f"❌ WSGI: Debug failed: {debug_e}")
    
    raise