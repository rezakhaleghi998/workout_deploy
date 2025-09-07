#!/bin/bash

echo "🚀 Starting Workout Calorie Predictor deployment..."

# Set environment variables for Railway
export DJANGO_SETTINGS_MODULE=fitness_tracker.settings
export PYTHONUNBUFFERED=1

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations
echo "🗃️ Running migrations..."
python manage.py migrate

# Create admin user (if it doesn't exist)
echo "👤 Setting up admin user..."
python manage.py shell << EOF
from fitness_app.models import User
try:
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@workoutpredictor.com', 'admin123')
        print("✅ Admin user created: admin/admin123")
    else:
        print("✅ Admin user already exists")
except Exception as e:
    print(f"⚠️ Admin user setup: {e}")
EOF

# Start the application
echo "🎉 Starting application server..."
echo "🔗 Admin panel will be available at: /admin/"
echo "🔑 Admin credentials: admin / admin123"

exec gunicorn fitness_tracker.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120
