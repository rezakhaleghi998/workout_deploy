from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction, connection
import os
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class Command(BaseCommand):
    help = 'Setup Railway deployment with admin user and database optimization'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of admin user',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚂 Starting Railway deployment setup...')
        )

        try:
            # Test database connection
            self.test_database_connection()
            
            # Create admin user
            self.create_admin_user(options.get('force', False))
            
            # Run database optimizations
            self.optimize_database()
            
            # Display deployment info
            self.display_deployment_info()
            
            self.stdout.write(
                self.style.SUCCESS('✅ Railway setup completed successfully!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Railway setup failed: {str(e)}')
            )
            raise

    def test_database_connection(self):
        """Test database connection and display info"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                db_version = cursor.fetchone()[0]
                
            self.stdout.write(
                self.style.SUCCESS(f'📊 Database connected: {db_version}')
            )
            
            # Check if we're using PostgreSQL
            if 'postgresql' in connection.vendor.lower():
                self.stdout.write(
                    self.style.SUCCESS('🐘 PostgreSQL database detected - Railway ready!')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Using {connection.vendor} database')
                )
                
        except Exception as e:
            raise Exception(f"Database connection failed: {str(e)}")

    def create_admin_user(self, force=False):
        """Create admin user from environment variables"""
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@workouttracker.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

        try:
            with transaction.atomic():
                if User.objects.filter(username=username).exists():
                    if force:
                        User.objects.filter(username=username).delete()
                        self.stdout.write(
                            self.style.WARNING(f'🔄 Existing admin user deleted')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'👤 Admin user "{username}" already exists')
                        )
                        return

                # Create superuser
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'👤 Admin user created successfully!')
                )
                self.stdout.write(f'   Username: {username}')
                self.stdout.write(f'   Email: {email}')
                self.stdout.write(f'   Password: {password}')
                
        except Exception as e:
            raise Exception(f"Failed to create admin user: {str(e)}")

    def optimize_database(self):
        """Run database optimizations for Railway PostgreSQL"""
        try:
            if 'postgresql' in connection.vendor.lower():
                with connection.cursor() as cursor:
                    # Analyze tables for query optimization
                    cursor.execute("ANALYZE;")
                    
                self.stdout.write(
                    self.style.SUCCESS('🔧 Database optimizations applied')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️  Skipping PostgreSQL optimizations (not PostgreSQL)')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Database optimization warning: {str(e)}')
            )

    def display_deployment_info(self):
        """Display Railway deployment information"""
        railway_env = os.environ.get('RAILWAY_ENVIRONMENT_NAME')
        railway_service = os.environ.get('RAILWAY_SERVICE_NAME', 'workout-tracker')
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('🚂 RAILWAY DEPLOYMENT INFO'))
        self.stdout.write('='*60)
        
        if railway_env:
            self.stdout.write(f'Environment: {railway_env}')
            self.stdout.write(f'Service: {railway_service}')
            self.stdout.write(f'URL: https://{railway_service}.railway.app')
        else:
            self.stdout.write('Running in local development mode')
            
        self.stdout.write(f'Admin Panel: /admin/')
        self.stdout.write(f'API Root: /api/')
        
        # Database info
        db_config = connection.settings_dict
        self.stdout.write(f'Database: {db_config.get("ENGINE", "Unknown").split(".")[-1]}')
        
        if 'postgresql' in connection.vendor.lower():
            self.stdout.write(f'DB Host: {db_config.get("HOST", "localhost")}')
            self.stdout.write(f'DB Name: {db_config.get("NAME", "Unknown")}')
            
        self.stdout.write('='*60 + '\n')
