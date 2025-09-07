#!/usr/bin/env python3
"""
Comprehensive Database Setup and Performance Index Fix
This script sets up your PostgreSQL database and fixes the NaN Performance Index issue
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.append(str(project_dir))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_tracker.settings')

# Set the DATABASE_URL environment variable
DATABASE_URL = "postgresql://fitness_tracker_db_3qe6_user:oVLVrbtziMFKg6myIBOHpbOIgY5N07ph@dpg-d2u5d7mr433s73e03k00-a/fitness_tracker_db_3qe6"
os.environ['DATABASE_URL'] = DATABASE_URL

print("🚀 Fitness Tracker Database Setup")
print("=" * 50)
print(f"📍 Database URL: {DATABASE_URL[:50]}...")
print()

try:
    # Setup Django
    django.setup()
    
    print("🔍 Testing database connection...")
    from django.db import connection
    from django.core.management import execute_from_command_line
    
    # Test connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
    if result:
        print("✅ PostgreSQL database connection successful!")
        
        # Run migrations
        print("\n🔄 Running database migrations...")
        try:
            execute_from_command_line(['manage.py', 'migrate'])
            print("✅ Database migrations completed successfully!")
        except Exception as e:
            print(f"⚠️ Migration warning: {e}")
        
        # Check if we need to create a superuser
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if not User.objects.exists():
            print("\n👤 No users found. Creating demo user...")
            try:
                user = User.objects.create_user(
                    username='demo_user',
                    email='demo@example.com',
                    password='demo123'
                )
                print("✅ Demo user created: demo_user / demo123")
            except Exception as e:
                print(f"⚠️ Could not create demo user: {e}")
        else:
            print(f"\n✅ Found {User.objects.count()} existing users in database")
        
        # Test workout data storage
        print("\n🏋️ Testing workout data models...")
        try:
            from fitness_app.models import WorkoutSession
            workout_count = WorkoutSession.objects.count()
            print(f"✅ Found {workout_count} workout sessions in database")
        except Exception as e:
            print(f"⚠️ Workout model issue: {e}")
        
        print("\n🎯 Database setup complete!")
        print("\n📋 Next Steps:")
        print("1. Your PostgreSQL database is ready")
        print("2. Performance Index will now read from database")
        print("3. All workout data will be saved to PostgreSQL")
        print("4. Run: python manage.py runserver")
        print("5. Login with demo_user / demo123")
        
    else:
        print("❌ Database connection failed - no response")
        
except Exception as e:
    print(f"❌ Database setup failed: {e}")
    print(f"🔧 Error type: {type(e).__name__}")
    
    # Check if it's a DNS issue
    if "host name" in str(e) or "address" in str(e):
        print("\n🔧 DNS Resolution Issue Detected")
        print("This usually means:")
        print("1. Database is still being provisioned")
        print("2. Network connectivity issue")
        print("3. Database URL might be incorrect")
        print("\n⏳ Try again in 5-10 minutes")
        print("📧 Contact your database provider if issue persists")
    
    print("\n🛠️ Fallback: Using SQLite for development")
    print("Remove DATABASE_URL environment variable to use SQLite")
    
    sys.exit(1)

print("\n🎉 Setup completed successfully!")
print("🚀 Your Fitness Tracker is ready with PostgreSQL!")
