#!/bin/bash

# Build script for Railway/Render deployment

echo "Starting build process..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
# Explicitly install gunicorn to ensure it's available
pip install gunicorn==21.2.0

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist
echo "Creating superuser..."
python manage.py create_superuser

# Verify gunicorn installation and location
echo "Verifying gunicorn installation..."
python -c "import gunicorn; print(f'Gunicorn installed at: {gunicorn.__file__}')"
python -c "import sys; print(f'Python path: {sys.executable}')"
pip show gunicorn
echo "Testing gunicorn module import..."
python -m gunicorn --version
echo "PATH: $PATH"

echo "Build completed successfully!"
