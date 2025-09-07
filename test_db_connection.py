#!/usr/bin/env python3
"""
Test PostgreSQL Database Connection
This script tests the connection to your PostgreSQL database
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

try:
    # Setup Django
    django.setup()
    
    # Test database connection
    from django.db import connection
    from django.core.management.color import make_style
    
    style = make_style('ERROR')
    
    print("🔍 Testing PostgreSQL database connection...")
    print(f"📍 Database URL: {DATABASE_URL[:50]}...")
    
    # Test connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
    if result:
        print("✅ PostgreSQL database connection successful!")
        
        # Get database info
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"📊 PostgreSQL Version: {version}")
        
        cursor.execute("SELECT current_database()")
        db_name = cursor.fetchone()[0]
        print(f"🗃️  Database Name: {db_name}")
        
        cursor.execute("SELECT current_user")
        db_user = cursor.fetchone()[0]
        print(f"👤 Database User: {db_user}")
        
        # Check if tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"📋 Existing tables: {len(tables)} found")
            for table in tables[:5]:  # Show first 5 tables
                print(f"   - {table[0]}")
            if len(tables) > 5:
                print(f"   ... and {len(tables) - 5} more")
        else:
            print("📋 No tables found - database is empty (ready for migrations)")
            
    else:
        print("❌ Database connection failed - no response")
        
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    print(f"🔧 Error type: {type(e).__name__}")
    
    # Common solutions
    print("\n🛠️  Troubleshooting:")
    print("1. Check if the database URL is correct")
    print("2. Verify network connectivity")
    print("3. Ensure database server is running")
    print("4. Check firewall settings")
    
    sys.exit(1)

print("\n🎯 Next steps:")
print("1. Run migrations: python manage.py migrate")
print("2. Create superuser: python manage.py createsuperuser")
print("3. Start the server: python manage.py runserver")
