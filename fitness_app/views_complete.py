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

# ============ API ROOT ============

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """API root endpoint"""
    return Response({
        'message': 'Fitness Tracker API',
        'endpoints': {
            'health': '/api/health/',
            'register': '/api/register/',
            'login': '/api/login/',
            'logout': '/api/logout/',
            'profile': '/api/profile/',
            'workouts': '/api/workouts/',
            'analytics': '/api/analytics/',
            'performance': '/api/performance/',
            'rankings': '/api/rankings/',
            'leaderboard': '/api/leaderboard/',
            'achievements': '/api/achievements/',
        }
    })

# ============ HEALTH CHECK ============

def health_check(request):
    """Health check for deployment"""
    return JsonResponse({'status': 'healthy', 'message': 'Application is running'})

# ============ MAIN VIEWS ============

def home(request):
    """Main application page"""
    return render(request, 'index.html')

# ============ AUTH VIEWS ============

@csrf_exempt
@require_http_methods(["POST"])
def register_user(request):
    """User registration"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already exists'}, status=400)
        
        user = User.objects.create_user(username=username, email=email, password=password)
        return JsonResponse({'message': 'User created successfully', 'user_id': user.id})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def login_user(request):
    """User login"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return JsonResponse({'message': 'Login successful', 'user_id': user.id})
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["POST"])
def logout_user(request):
    """User logout"""
    logout(request)
    return JsonResponse({'message': 'Logout successful'})

@login_required
def user_profile(request):
    """Get user profile"""
    user = request.user
    return JsonResponse({
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'date_joined': user.date_joined.isoformat() if user.date_joined else None
    })

# ============ WORKOUT VIEWS ============

@login_required
def workout_sessions(request):
    """Get workout sessions for user"""
    if request.method == 'GET':
        sessions = WorkoutSession.objects.filter(user=request.user).order_by('-date')[:20]
        return JsonResponse({
            'sessions': [{
                'id': session.id,
                'date': session.date.isoformat() if session.date else None,
                'duration': session.duration,
                'calories_burned': session.calories_burned,
                'exercise_type': session.exercise_type
            } for session in sessions]
        })
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            session = WorkoutSession.objects.create(
                user=request.user,
                exercise_type=data.get('exercise_type', ''),
                duration=data.get('duration', 0),
                calories_burned=data.get('calories_burned', 0)
            )
            return JsonResponse({'message': 'Workout session created', 'session_id': session.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@login_required 
def workout_analytics(request):
    """Get workout analytics"""
    try:
        analytics = WorkoutAnalysis.objects.filter(user=request.user).order_by('-date')[:10]
        return JsonResponse({
            'analytics': [{
                'id': analysis.id,
                'date': analysis.date.isoformat() if analysis.date else None,
                'total_workouts': analysis.total_workouts,
                'total_duration': analysis.total_duration,
                'total_calories': analysis.total_calories,
                'average_intensity': analysis.average_intensity
            } for analysis in analytics]
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ============ PERFORMANCE VIEWS ============

@login_required
def performance_metrics(request):
    """Get performance metrics"""
    try:
        metrics = FitnessPerformanceIndex.objects.filter(user=request.user).order_by('-date')[:10]
        return JsonResponse({
            'metrics': [{
                'id': metric.id,
                'date': metric.date.isoformat() if metric.date else None,
                'performance_score': metric.performance_score,
                'strength_index': metric.strength_index,
                'endurance_index': metric.endurance_index,
                'flexibility_index': metric.flexibility_index
            } for metric in metrics]
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ============ RANKING VIEWS ============

@login_required
def user_rankings(request):
    """Get user rankings"""
    try:
        # Simple ranking based on total workouts
        user_workouts = WorkoutSession.objects.filter(user=request.user).count()
        total_users = User.objects.count()
        
        return JsonResponse({
            'user_workouts': user_workouts,
            'total_users': total_users,
            'rank': 'N/A'  # Simplified for now
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def leaderboard(request):
    """Get leaderboard"""
    try:
        # Simple leaderboard based on workout count
        from django.db.models import Count
        
        top_users = User.objects.annotate(
            workout_count=Count('workoutsession')
        ).order_by('-workout_count')[:10]
        
        return JsonResponse({
            'leaderboard': [{
                'username': user.username,
                'workout_count': user.workout_count
            } for user in top_users]
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def user_achievements(request):
    """Get user achievements"""
    try:
        workout_count = WorkoutSession.objects.filter(user=request.user).count()
        achievements = []
        
        if workout_count >= 1:
            achievements.append('First Workout')
        if workout_count >= 10:
            achievements.append('10 Workouts')
        if workout_count >= 50:
            achievements.append('50 Workouts')
        if workout_count >= 100:
            achievements.append('Century Club')
            
        return JsonResponse({'achievements': achievements})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
