#!/bin/bash

echo "==> Starting build process..."

# Simple pip install with no cache to avoid build issues
echo "==> Installing dependencies..."
pip install --no-cache-dir -r requirements.txt

# Collect static files
echo "==> Collecting static files..."
python manage.py collectstatic --noinput

# Apply migrations
echo "==> Running migrations..."
python manage.py migrate

echo "==> Build completed successfully!"