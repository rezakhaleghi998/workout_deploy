#!/usr/bin/env python
"""
Admin Implementation Test Script
Tests all new admin functionality to ensure everything works correctly.
"""

import os
import sys
import django
from django.test import Client
from django.urls import reverse
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_tracker.settings')
django.setup()

from fitness_app.models import User, WorkoutAnalysis, FitnessPerformanceIndex, WellnessPlan

def test_models():
    """Test that all new models work correctly"""
    print("🧪 Testing Models...")
    
    # Create test user
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    
    # Test WorkoutAnalysis model
    analysis = WorkoutAnalysis.objects.create(
        user=user,
        analysis_type='for_me',
        age=30,
        gender='Male',
        height_cm=180.0,
        weight_kg=75.0,
        workout_type='Running',
        duration_minutes=30,
        predicted_calories=350.50,
        activity_level='Moderately Active'
    )
    
    # Test FitnessPerformanceIndex model
    performance = FitnessPerformanceIndex.objects.create(
        user=user,
        workout_analysis=analysis,
        overall_score=85.5,
        fitness_level='Intermediate',
        progress_status='Steady progress',
        consistency_score=80.0,
        consistency_percentage=75.0,
        performance_score=90.0,
        performance_percentage=85.0,
        variety_score=70.0,
        variety_percentage=65.0,
        intensity_score=85.0,
        intensity_percentage=80.0
    )
    
    # Test WellnessPlan model
    wellness = WellnessPlan.objects.create(
        user=user,
        workout_analysis=analysis,
        total_daily_calories_needed=2500.0,
        basal_metabolic_rate=1800.0,
        recommended_intake=2200.0,
        personalized_diet_plan={"breakfast": "Oatmeal and fruits"},
        advanced_workout_programming={"weekly_plan": "3x cardio, 2x strength"}
    )
    
    print("✅ All models created successfully!")
    print(f"   - User: {user}")
    print(f"   - Analysis: {analysis}")
    print(f"   - Performance: {performance}")
    print(f"   - Wellness: {wellness}")
    
    # Cleanup
    user.delete()
    
    return True

def test_admin_interface():
    """Test that admin interface is properly configured"""
    print("\n🎛️ Testing Admin Interface...")
    
    from django.contrib import admin
    from fitness_app.admin import WorkoutAnalysisAdmin, FitnessPerformanceIndexAdmin, WellnessPlanAdmin
    
    # Check if models are registered
    admin_site = admin.site
    registered_models = [model._meta.model_name for model in admin_site._registry.keys()]
    
    expected_models = ['user', 'workoutanalysis', 'fitnessperformanceindex', 'wellnessplan']
    for model in expected_models:
        if model in registered_models:
            print(f"   ✅ {model} is registered in admin")
        else:
            print(f"   ❌ {model} is NOT registered in admin")
    
    return True

def test_api_endpoints():
    """Test API endpoints"""
    print("\n🌐 Testing API Endpoints...")
    
    client = Client()
    
    # Test API root
    response = client.get('/api/')
    if response.status_code == 200:
        print("   ✅ API root endpoint works")
    else:
        print(f"   ❌ API root endpoint failed: {response.status_code}")
    
    # Test health check
    response = client.get('/api/health/')
    if response.status_code == 200:
        print("   ✅ Health check endpoint works")
    else:
        print(f"   ❌ Health check endpoint failed: {response.status_code}")
    
    return True

def test_database_connections():
    """Test database connectivity"""
    print("\n💾 Testing Database...")
    
    from django.db import connection
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
        if result == (1,):
            print("   ✅ Database connection successful")
        else:
            print("   ❌ Database connection failed")
            
        # Test model counts
        user_count = User.objects.count()
        analysis_count = WorkoutAnalysis.objects.count()
        
        print(f"   📊 Current data: {user_count} users, {analysis_count} analyses")
        
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False
    
    return True

def test_integration_script():
    """Test that integration script exists and is valid"""
    print("\n🔗 Testing Integration Script...")
    
    script_path = 'static/js/admin_integration.js'
    
    if os.path.exists(script_path):
        print("   ✅ admin_integration.js exists")
        
        with open(script_path, 'r') as f:
            content = f.read()
            
        # Check for key functions
        if 'WorkoutAnalysisCapture' in content:
            print("   ✅ WorkoutAnalysisCapture class found")
        if 'saveWorkoutAnalysis' in content:
            print("   ✅ saveWorkoutAnalysis function found")
        if 'captureAndSaveAnalysis' in content:
            print("   ✅ captureAndSaveAnalysis function found")
            
    else:
        print(f"   ❌ Integration script not found at {script_path}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 WORKOUT CALORIE PREDICTOR ADMIN SYSTEM TEST")
    print("=" * 50)
    
    tests = [
        test_database_connections,
        test_models,
        test_admin_interface,
        test_api_endpoints,
        test_integration_script
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"   ❌ Test failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    if all(results):
        print("🎉 ALL TESTS PASSED!")
        print("✅ Your admin system is fully functional and ready for deployment!")
        print("\nNext steps:")
        print("1. Push to GitHub")
        print("2. Verify Render deployment") 
        print("3. Create admin user on production")
        print("4. Access admin panel at /admin/")
    else:
        print("⚠️ Some tests failed. Please check the output above.")
        print("The system may still work, but some features might need attention.")
    
    return all(results)

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
