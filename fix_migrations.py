#!/usr/bin/env python
"""
Django Migration Dependency Fix Script
Resolves InconsistentMigrationHistory error for Render deployment
Specifically handles conflicts between custom User model and admin migrations
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.db import connection
from django.core.management.base import BaseCommand
from django.conf import settings

def setup_django():
    """Set up Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_tracker.settings')
    django.setup()

def backup_database():
    """Create a backup of the current database state"""
    print("📦 Creating database backup...")
    try:
        # For SQLite (local development)
        if 'sqlite' in settings.DATABASES['default']['ENGINE']:
            import shutil
            db_path = settings.DATABASES['default']['NAME']
            backup_path = f"{db_path}.backup"
            if os.path.exists(db_path):
                shutil.copy2(db_path, backup_path)
                print(f"✅ Local SQLite backup created: {backup_path}")
        else:
            print("⚠️  For production database, ensure you have a backup from your hosting provider")
            
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False
    return True

def check_migration_state():
    """Check current migration state"""
    print("\n🔍 Checking current migration state...")
    
    try:
        from django.db.migrations.executor import MigrationExecutor
        from django.db import connection
        
        executor = MigrationExecutor(connection)
        applied_migrations = executor.loader.applied_migrations
        
        print(f"Applied migrations count: {len(applied_migrations)}")
        
        # Check for problematic admin migrations
        admin_migrations = [m for m in applied_migrations if m[0] == 'admin']
        fitness_migrations = [m for m in applied_migrations if m[0] == 'fitness_app']
        
        print(f"Admin migrations applied: {len(admin_migrations)}")
        print(f"Fitness_app migrations applied: {len(fitness_migrations)}")
        
        if admin_migrations and not fitness_migrations:
            print("⚠️  ISSUE DETECTED: Admin migrations applied before fitness_app migrations")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Migration state check failed: {e}")
        return False

def fix_migration_dependencies():
    """Fix migration dependency issues"""
    print("\n🔧 Fixing migration dependencies...")
    
    try:
        # Step 1: Fake unapply admin migrations
        print("Step 1: Fake unapplying admin migrations...")
        execute_from_command_line([
            'manage.py', 'migrate', 'admin', 'zero', '--fake'
        ])
        
        # Step 2: Fake unapply auth migrations that depend on User model
        print("Step 2: Fake unapplying problematic auth migrations...")
        execute_from_command_line([
            'manage.py', 'migrate', 'auth', '0011', '--fake'
        ])
        
        # Step 3: Apply fitness_app migrations first
        print("Step 3: Applying fitness_app migrations...")
        execute_from_command_line([
            'manage.py', 'migrate', 'fitness_app'
        ])
        
        # Step 4: Apply auth migrations
        print("Step 4: Applying auth migrations...")
        execute_from_command_line([
            'manage.py', 'migrate', 'auth'
        ])
        
        # Step 5: Apply admin migrations
        print("Step 5: Applying admin migrations...")
        execute_from_command_line([
            'manage.py', 'migrate', 'admin'
        ])
        
        # Step 6: Apply all remaining migrations
        print("Step 6: Applying all remaining migrations...")
        execute_from_command_line([
            'manage.py', 'migrate'
        ])
        
        print("✅ Migration dependencies fixed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration fix failed: {e}")
        return False

def reset_migrations_completely():
    """Complete migration reset (more aggressive approach)"""
    print("\n🔄 Performing complete migration reset...")
    
    try:
        # Step 1: Fake unapply all migrations
        print("Step 1: Fake unapplying all migrations...")
        execute_from_command_line([
            'manage.py', 'migrate', '--fake', 'fitness_app', 'zero'
        ])
        execute_from_command_line([
            'manage.py', 'migrate', '--fake', 'admin', 'zero'
        ])
        execute_from_command_line([
            'manage.py', 'migrate', '--fake', 'auth', 'zero'
        ])
        execute_from_command_line([
            'manage.py', 'migrate', '--fake', 'contenttypes', 'zero'
        ])
        execute_from_command_line([
            'manage.py', 'migrate', '--fake', 'sessions', 'zero'
        ])
        
        # Step 2: Apply migrations in correct order
        print("Step 2: Applying migrations in correct order...")
        
        # contenttypes first (required by auth)
        execute_from_command_line([
            'manage.py', 'migrate', 'contenttypes'
        ])
        
        # fitness_app (contains custom User model)
        execute_from_command_line([
            'manage.py', 'migrate', 'fitness_app'
        ])
        
        # auth (now can reference custom User)
        execute_from_command_line([
            'manage.py', 'migrate', 'auth'
        ])
        
        # admin (depends on auth and User model)
        execute_from_command_line([
            'manage.py', 'migrate', 'admin'
        ])
        
        # sessions
        execute_from_command_line([
            'manage.py', 'migrate', 'sessions'
        ])
        
        # all remaining
        execute_from_command_line([
            'manage.py', 'migrate'
        ])
        
        print("✅ Complete migration reset successful!")
        return True
        
    except Exception as e:
        print(f"❌ Complete reset failed: {e}")
        return False

def main():
    """Main execution function"""
    print("🚀 Django Migration Dependency Fix Tool")
    print("="*50)
    
    # Setup Django
    setup_django()
    
    # Create backup
    if not backup_database():
        response = input("⚠️  Backup failed. Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("❌ Aborted for safety")
            return
    
    # Check current state
    if check_migration_state():
        print("✅ Migration state looks good. No fixes needed.")
        return
    
    print("\n📋 Choose fix strategy:")
    print("1. Try gentle dependency fix (recommended)")
    print("2. Complete migration reset (more aggressive)")
    print("3. Exit")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == '1':
        success = fix_migration_dependencies()
    elif choice == '2':
        confirm = input("⚠️  This will reset all migrations. Continue? (y/N): ")
        if confirm.lower() == 'y':
            success = reset_migrations_completely()
        else:
            print("❌ Aborted")
            return
    else:
        print("👋 Exiting")
        return
    
    if success:
        print("\n✅ Migration fix completed successfully!")
        print("\n📋 Next steps for deployment:")
        print("1. Test locally: python manage.py runserver")
        print("2. Commit changes: git add . && git commit -m 'Fix migration dependencies'")
        print("3. Deploy to Render")
        print("\n⚠️  If deployment still fails, check Render logs for specific errors")
    else:
        print("\n❌ Migration fix failed. Check error messages above.")
        print("💡 Consider restoring from backup and trying the alternative strategy")

if __name__ == '__main__':
    main()
