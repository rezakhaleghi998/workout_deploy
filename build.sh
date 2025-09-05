#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🚀 Starting build process..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --no-input

# Run migrations (simplified)
echo "🗄️ Running migrations..."
python manage.py migrate --no-input

# Create superuser if needed
echo "👤 Creating superuser..."
python manage.py create_superuser

echo "✅ Build completed successfully!"