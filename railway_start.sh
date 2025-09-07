#!/bin/bash

echo "🚂 Starting Railway deployment..."

# Run migrations
echo "📦 Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
echo "👤 Setting up admin user..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@railway.com', 'admin123')
    print('✅ Admin user created: admin/admin123')
else:
    print('✅ Admin user already exists')
"

# Start the server
echo "🚀 Starting Gunicorn server..."
exec gunicorn fitness_tracker.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
