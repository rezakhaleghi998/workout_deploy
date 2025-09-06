#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_tracker.settings')
django.setup()

from fitness_app.models import User

# Create test user
try:
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    if created:
        user.set_password('testpass123')
        user.save()
        print("✅ Test user created successfully")
        print(f"Username: testuser")
        print(f"Password: testpass123")
    else:
        print("✅ Test user already exists")
        print(f"Username: testuser")
        print(f"Password: testpass123")
        
except Exception as e:
    print(f"❌ Error creating user: {e}")
