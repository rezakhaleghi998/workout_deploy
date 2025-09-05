#!/bin/bash
set -o errexit  # Exit on error

echo "==> Starting build process..."

# Upgrade pip first
echo "==> Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "==> Installing dependencies..."
pip install -r requirements.txt

# Verify Django installation
echo "==> Verifying Django installation..."
python -c "import django; print(f'Django version: {django.get_version()}')"

# Collect static files
echo "==> Collecting static files..."
python manage.py collectstatic --noinput

# Apply migrations
echo "==> Running migrations..."
python manage.py migrate

# Create superuser
echo "==> Setting up superuser..."
python manage.py create_superuser

echo "==> Build completed successfully!"