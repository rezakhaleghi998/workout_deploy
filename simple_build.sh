#!/usr/bin/env bash
# Simple and reliable Render build script

set -o errexit

echo "🚀 Starting simple Render build..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Simple migration
echo "🔄 Running migrations..."
python manage.py migrate --noinput

echo "✅ Build completed successfully!"
