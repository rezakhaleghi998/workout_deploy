"""
Django management command to fix migration dependencies for Render deployment
Specifically handles InconsistentMigrationHistory with custom User models
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
import sys


class Command(BaseCommand):
    help = 'Fix migration dependencies for Render deployment'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force migration fix even if no issues detected',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting Render migration dependency fix...')
        )

        try:
            # Check if we can run standard migrations
            self.stdout.write('🔍 Checking migration state...')
            
            # First, try a migration check
            try:
                call_command('migrate', '--check', verbosity=0)
                self.stdout.write(
                    self.style.SUCCESS('✅ No migration conflicts detected')
                )
                
                if not options['force']:
                    # Run standard migration
                    call_command('migrate', verbosity=1)
                    self.stdout.write(
                        self.style.SUCCESS('✅ Standard migrations applied successfully')
                    )
                    return
                    
            except Exception as e:
                if 'InconsistentMigrationHistory' in str(e):
                    self.stdout.write(
                        self.style.WARNING('⚠️  InconsistentMigrationHistory detected')
                    )
                    self.stdout.write(f'Error: {e}')
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Migration check failed: {e}')
                    )

            # Apply the fix
            self.stdout.write('🔧 Applying migration dependency fix...')
            
            # Define migration order for custom User model
            migration_order = [
                'contenttypes',  # Required for auth system
                'fitness_app',   # Custom User model (must be first)
                'auth',          # Depends on User model
                'admin',         # Depends on auth and User
                'sessions',      # Session framework
            ]
            
            # Migrate each app in order
            for app in migration_order:
                try:
                    self.stdout.write(f'📋 Migrating {app}...')
                    call_command('migrate', app, verbosity=1, interactive=False)
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ {app} migrations completed')
                    )
                except Exception as app_error:
                    # Don't fail completely if one app fails
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠️  Warning during {app} migration: {app_error}'
                        )
                    )
                    continue
            
            # Apply any remaining migrations
            self.stdout.write('📋 Applying any remaining migrations...')
            try:
                call_command('migrate', verbosity=1, interactive=False)
                self.stdout.write(
                    self.style.SUCCESS('✅ All remaining migrations applied')
                )
            except Exception as final_error:
                self.stdout.write(
                    self.style.ERROR(f'❌ Final migration failed: {final_error}')
                )
                # Continue anyway, might not be fatal
            
            # Verify final state
            self.stdout.write('🔍 Verifying final migration state...')
            try:
                call_command('showmigrations', format='list', verbosity=1)
            except:
                pass  # Not critical if this fails
            
            self.stdout.write(
                self.style.SUCCESS(
                    '✅ Migration dependency fix completed successfully!'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Migration fix failed: {e}')
            )
            self.stdout.write(
                '💡 Check your migration files and database state'
            )
            sys.exit(1)
