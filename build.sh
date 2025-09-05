#!/bin/bash

# Build script for Railway/Render deployment

echo "Starting build process..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

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
which gunicorn || echo "Gunicorn not in PATH, checking pip show..."
pip show gunicorn | grep Location
echo "Python executable: $(which python)"

echo "Build completed successfully!"
