from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.db import models
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import User, WorkoutSession, WorkoutAnalysis, FitnessPerformanceIndex, WellnessPlan

# ============ MAIN VIEWS ============

def home(request):
    """Main application page"""
    return render(request, 'index.html')

def health_check(request):
    """Health check endpoint for Railway"""
    return JsonResponse({'status': 'healthy', 'service': 'workout_tracker'})

# ============ API VIEWS ============

@api_view(['POST'])
@permission_classes([AllowAny])
def analyze_workout(request):
    """Analyze workout data and return calorie prediction"""
    try:
        data = request.data
        
        # Basic workout analysis
        workout_type = data.get('workout_type', 'general')
        duration = int(data.get('duration_minutes', 30))
        intensity = data.get('intensity_level', 'moderate')
        
        # Simple calorie calculation
        base_calories = {
            'running': 10,
            'cycling': 8,
            'swimming': 12,
            'weightlifting': 6,
            'yoga': 3,
            'walking': 4
        }
        
        intensity_multiplier = {
            'low': 0.8,
            'moderate': 1.0,
            'high': 1.3,
            'extreme': 1.6
        }
        
        calories = (base_calories.get(workout_type.lower(), 7) * 
                   duration * 
                   intensity_multiplier.get(intensity, 1.0))
        
        # Create workout analysis if user is authenticated
        if request.user.is_authenticated:
            WorkoutAnalysis.objects.create(
                user=request.user,
                workout_type=workout_type,
                duration_minutes=duration,
                intensity_level=intensity,
                calories_burned=calories,
                performance_score=min(calories / 10, 100)
            )
        
        return Response({
            'success': True,
            'calories_burned': round(calories, 2),
            'workout_type': workout_type,
            'duration_minutes': duration,
            'intensity_level': intensity,
            'performance_score': min(calories / 10, 100)
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=400)

@api_view(['GET'])
@permission_classes([AllowAny])
def user_stats(request):
    """Get user workout statistics"""
    try:
        if not request.user.is_authenticated:
            return Response({
                'total_workouts': 0,
                'total_calories': 0,
                'avg_performance': 0
            })
        
        analyses = WorkoutAnalysis.objects.filter(user=request.user)
        
        return Response({
            'total_workouts': analyses.count(),
            'total_calories': sum(a.calories_burned for a in analyses),
            'avg_performance': analyses.aggregate(
                avg=models.Avg('performance_score')
            )['avg'] or 0
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=400)

# ============ SIMPLE AUTH VIEWS ============

@csrf_exempt
@require_http_methods(["POST"])
def simple_login(request):
    """Simple login endpoint"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return JsonResponse({
                'success': True,
                'user': {
                    'username': user.username,
                    'email': user.email
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Invalid credentials'
            }, status=401)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@require_http_methods(["POST"])
def simple_logout(request):
    """Simple logout endpoint"""
    logout(request)
    return JsonResponse({'success': True})

# ============ LEGACY ENDPOINTS FOR COMPATIBILITY ============

@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_performance_data(request):
    """Legacy endpoint for performance data"""
    return Response({
        'performance_index': 75.5,
        'trend': 'improving',
        'last_updated': '2025-09-08'
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def save_workout_analysis(request):
    """Legacy endpoint for saving workout analysis"""
    return analyze_workout(request)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_recommendations(request):
    """Legacy endpoint for recommendations"""
    return Response({
        'recommendations': [
            'Try increasing workout intensity',
            'Add more cardio exercises',
            'Focus on consistency'
        ]
    })
