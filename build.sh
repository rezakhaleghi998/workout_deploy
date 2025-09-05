#!/bin/bash

# Build script for Render deployment

echo "Starting build process..."

# Upgrade pip and install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Set Python path
export PYTHONPATH="${PYTHONPATH}:/opt/render/project/src"

# Make scripts executable
chmod +x start.sh

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist
echo "Creating superuser..."
python manage.py create_superuser

echo "Build completed successfully!"