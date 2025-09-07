#!/bin/bash
# Railway Deployment Script
# This script sets up your Django app with admin system on Railway (100% FREE)

echo "🚀 Deploying Workout Calorie Predictor with Admin System to Railway..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "🗃️ Setting up database..."
python manage.py migrate

# Create superuser for admin access
echo "👤 Creating admin user..."
python manage.py shell << EOF
from fitness_app.models import User
try:
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@workoutpredictor.com', 'admin123')
        print("✅ Admin user created: admin/admin123")
    else:
        print("✅ Admin user already exists")
except Exception as e:
    print(f"⚠️ Admin user creation error: {e}")
EOF

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create some test data for demonstration
echo "📊 Creating test data..."
python manage.py shell << EOF
from fitness_app.models import User, WorkoutAnalysis
try:
    # Create test user if not exists
    test_user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    if created:
        test_user.set_password('testpass123')
        test_user.save()
    
    # Create sample workout analysis
    if not WorkoutAnalysis.objects.filter(user=test_user).exists():
        WorkoutAnalysis.objects.create(
            user=test_user,
            analysis_type='for_me',
            age=30,
            gender='Male',
            height_cm=180.0,
            weight_kg=75.0,
            workout_type='Running',
            duration_minutes=30,
            predicted_calories=350.50,
            activity_level='Moderately Active',
            efficiency_grade='B+',
            fitness_performance_index=85.5
        )
        print("✅ Sample workout analysis created")
    
    print(f"✅ Total users: {User.objects.count()}")
    print(f"✅ Total analyses: {WorkoutAnalysis.objects.count()}")
    
except Exception as e:
    print(f"⚠️ Test data creation error: {e}")
EOF

echo "🎉 Deployment complete!"
echo ""
echo "🔗 Access your app:"
echo "   • Main App: https://your-railway-url.up.railway.app"
echo "   • Admin Panel: https://your-railway-url.up.railway.app/admin/"
echo "   • Admin Login: admin / admin123"
echo ""
echo "💾 Database Access:"
echo "   • Use Railway's built-in terminal (100% FREE)"
echo "   • Run: python manage.py shell"
echo "   • Query your data with Django ORM"
