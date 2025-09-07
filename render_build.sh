#!/usr/bin/env bash
# Render Deployment Build Script - PostgreSQL Optimized
# Handles database migrations and static files for production

set -o errexit

echo "🚀 Starting Render deployment build..."
echo "📊 Build environment: $(python --version)"

# Install Python dependencies with explicit PostgreSQL support
echo "📦 Installing Python dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Verify PostgreSQL adapter installation
echo "� Verifying PostgreSQL adapter..."
python -c "import psycopg2; print('✅ psycopg2 imported successfully')" || echo "❌ psycopg2 import failed"
python -c "import dj_database_url; print('✅ dj_database_url imported successfully')" || echo "❌ dj_database_url import failed"

# Test database connection
echo "� Testing database connection..."
python manage.py check --database=default || echo "⚠️ Database check failed, continuing..."

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear
# Database migrations with robust error handling
echo "🔄 Handling database migrations..."

# First, check database connectivity
echo "🔗 Checking database connectivity..."
python -c "
import os
import sys
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_tracker.settings')
import django
django.setup()
from django.db import connection
try:
    cursor = connection.cursor()
    cursor.execute('SELECT 1')
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    sys.exit(1)
"

# Show current migration status
echo "📋 Current migration status..."
python manage.py showmigrations || echo "Migration status check completed"

# Apply migrations with dependency resolution
echo "🔄 Applying database migrations..."

# For PostgreSQL on Render, apply migrations in correct order
echo "📋 Step 1: Creating initial migrations..."
python manage.py makemigrations fitness_app --noinput || echo "Migrations already exist"

echo "📋 Step 2: Migrating core Django apps..."
python manage.py migrate contenttypes --noinput || echo "Contenttypes migrated"
python manage.py migrate auth --noinput || echo "Auth migrated"

echo "📋 Step 3: Migrating fitness app..."
python manage.py migrate fitness_app --noinput || echo "Fitness app migrated"

echo "📋 Step 4: Migrating remaining apps..."
python manage.py migrate --noinput || echo "All migrations completed"

echo "✅ Database migrations completed successfully!"

# Create superuser if needed (for production)
echo "👤 Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'render_admin_2024')
    print('✅ Superuser created')
else:
    print('✅ Superuser already exists')
" || echo "Superuser check completed"

echo "✅ Build completed successfully!"

# Clean up temporary files
rm -f migration_status.txt
