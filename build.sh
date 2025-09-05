#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Starting build process..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# RENDER-SPECIFIC MIGRATION FIX
# Handle the InconsistentMigrationHistory error for custom User model
echo "Fixing migration dependencies for Render deployment..."
python manage.py fix_render_migrations

# Create superuser if it doesn't exist
echo "Creating superuser..."
python manage.py create_superuser

echo "Build completed successfully!"