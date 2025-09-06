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
# Database migrations with simple approach
echo "� Handling database migrations..."

# Simple migration approach for Render
echo "📋 Running Django migrations..."
python manage.py migrate --noinput

echo "✅ Database migrations completed!"

echo "✅ Build completed successfully!"

# Clean up temporary files
rm -f migration_status.txt
