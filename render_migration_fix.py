# Render Deployment Migration Fix
# This script handles the specific case where Render's database has migration inconsistencies

import os
import sys
import django
from django.core.management import execute_from_command_line, call_command
from django.db import connection
from django.conf import settings

def setup_django():
    """Set up Django environment for Render deployment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_tracker.settings')
    django.setup()

def check_database_exists():
    """Check if database tables exist"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='django_migrations';
            """)
            return cursor.fetchone() is not None
    except:
        # For PostgreSQL or other databases
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'django_migrations'
                    );
                """)
                return cursor.fetchone()[0]
        except:
            return False

def fix_render_migration_conflict():
    """
    Fix migration conflicts specifically for Render deployment
    This handles the case where admin migrations are applied before custom User model
    """
    print("🔧 Fixing Render migration conflicts...")
    
    try:
        # Check if database exists and has migration table
        if not check_database_exists():
            print("📝 Fresh database detected. Applying migrations in correct order...")
            
            # Apply migrations in dependency order for fresh database
            apps_order = ['contenttypes', 'fitness_app', 'auth', 'admin', 'sessions']
            
            for app in apps_order:
                try:
                    print(f"📋 Migrating {app}...")
                    call_command('migrate', app, verbosity=1, interactive=False)
                except Exception as e:
                    print(f"⚠️  Warning during {app} migration: {e}")
                    continue
            
            # Apply any remaining migrations
            print("📋 Applying remaining migrations...")
            call_command('migrate', verbosity=1, interactive=False)
            
        else:
            print("📝 Existing database detected. Checking migration state...")
            
            # For existing database, try gentle approach
            try:
                # Check migration status
                call_command('showmigrations', format='list')
                
                # Try standard migration first
                call_command('migrate', verbosity=1, interactive=False)
                print("✅ Standard migration successful")
                
            except Exception as e:
                if "InconsistentMigrationHistory" in str(e):
                    print("⚠️  InconsistentMigrationHistory detected. Attempting recovery...")
                    
                    # For production database, we can't fake unapply
                    # Instead, try to migrate specific problematic apps
                    try:
                        # Try migrating fitness_app first (custom User model)
                        call_command('migrate', 'fitness_app', verbosity=1, interactive=False)
                        
                        # Then auth and admin
                        call_command('migrate', 'auth', verbosity=1, interactive=False)
                        call_command('migrate', 'admin', verbosity=1, interactive=False)
                        
                        # Finally, all remaining
                        call_command('migrate', verbosity=1, interactive=False)
                        
                        print("✅ Migration conflict resolved")
                        
                    except Exception as final_error:
                        print(f"❌ Final migration attempt failed: {final_error}")
                        print("💡 This may require manual database intervention")
                        return False
                else:
                    print(f"❌ Migration failed with error: {e}")
                    return False
        
        return True
        
    except Exception as e:
        print(f"❌ Migration fix failed: {e}")
        return False

def main():
    """Main function for Render deployment"""
    print("🚀 Render Django Migration Fix")
    print("=" * 40)
    
    # Set up Django
    setup_django()
    
    # Fix migration conflicts
    success = fix_render_migration_conflict()
    
    if success:
        print("\n✅ Migration fix completed successfully!")
        
        # Verify final state
        print("\n🔍 Final migration verification:")
        try:
            call_command('showmigrations', format='list')
        except:
            pass
            
    else:
        print("\n❌ Migration fix failed")
        print("💡 Check Render deployment logs for specific error details")
        sys.exit(1)

if __name__ == '__main__':
    main()
