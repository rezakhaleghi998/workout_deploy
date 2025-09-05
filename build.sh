#!/bin/bash

# Build script for Railway/Render deployment

echo "Starting build process..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
# Explicitly install critical dependencies to ensure they're available
pip install Django==4.2.7
pip install gunicorn==21.2.0
pip install dj-database-url==2.1.0
pip install psycopg2-binary==2.9.7
pip install whitenoise==6.6.0

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist
echo "Creating superuser..."
python manage.py create_superuser

# Verify critical dependencies installation
echo "Verifying critical dependencies..."
python -c "import django; print(f'✅ Django version: {django.get_version()}')"
python -c "import gunicorn; print(f'✅ Gunicorn version: {gunicorn.__version__}')"
python -c "import dj_database_url; print('✅ dj-database-url imported successfully')"
python -c "import psycopg2; print(f'✅ psycopg2 version: {psycopg2.__version__}')"
python -c "import whitenoise; print('✅ whitenoise imported successfully')"
python -c "import rest_framework; print('✅ DRF imported successfully')"

# Verify Django settings import
echo "Testing Django settings import..."
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_tracker.settings'); import django; django.setup(); print('✅ Django settings loaded successfully')"

# Verify gunicorn installation and location
echo "Verifying gunicorn installation..."
python -c "import gunicorn; print(f'Gunicorn installed at: {gunicorn.__file__}')"
python -c "import sys; print(f'Python path: {sys.executable}')"
echo "Testing gunicorn module import..."
python -m gunicorn --version

# Test WSGI application import
echo "Testing WSGI application import..."
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_tracker.settings'); from fitness_tracker.wsgi import application; print('✅ WSGI application imported successfully')"

# Run comprehensive deployment tests
echo "Running comprehensive deployment tests..."
python test_deployment.py

echo "🎉 Build completed successfully!"
