#!/bin/bash

echo "🚂 Starting Railway deployment..."

# Run migrations
echo "📦 Running database migrations..."
python manage.py migrate --noinput

# Start the server with correct syntax
echo "🚀 Starting Gunicorn server..."
exec gunicorn fitness_tracker.wsgi:application --bind 0.0.0.0:${PORT:-8000}
