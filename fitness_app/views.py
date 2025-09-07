from django.shortcuts import render
from django.contrib.auth import authenticate
from django.db import transaction, connection
from django.db.models import Q, Sum, Avg, Count
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import User, UserProfile, WorkoutSession, PerformanceMetrics, UserRanking, Achievement
from .serializers import (
    UserRegistrationSerializer, UserSerializer, UserProfileSerializer,
    WorkoutSessionSerializer, PerformanceMetricsSerializer,
    UserRankingSerializer, AchievementSerializer
)
from .db_retry import db_retry, ensure_db_connection

# ============ HEALTH CHECK ============

def health_check(request):
    """Health check endpoint for Render deployment"""
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Test basic functionality
        user_count = User.objects.count()
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected',
            'user_count': user_count,
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy', 
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=500)

# ============ MAIN VIEWS ============

def home_view(request):
    """Serve the main fitness tracker application"""
    return render(request, 'index.html')

def login_view(request):
    """Serve the login page"""
    return render(request, 'login.html')

# ============ AUTHENTICATION VIEWS ============

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Register a new user"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        with transaction.atomic():
            user = serializer.save()
            # Create user profile
            UserProfile.objects.get_or_create(user=user)
            # Create user ranking
            UserRanking.objects.get_or_create(user=user)
            # Create auth token
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key,
                'message': 'User registered successfully'
            }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """Login user and return token"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if username and password:
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key,
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response({
        'error': 'Username and password required'
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """Logout user by deleting token"""
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    except:
        return Response({'error': 'Error logging out'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT'])
@permission_classes([AllowAny])  # Allow unauthenticated access for demo mode
@db_retry(max_retries=3, delay=1)
def user_profile(request):
    """Get or update user profile with database retry logic"""
    try:
        # For demo purposes, we'll use a default profile approach
        # In production with authentication, this would use request.user
        
        if request.method == 'GET':
            # Try to get or create a default profile for demo
            try:
                profile = UserProfile.objects.first()
                if not profile:
                    # Create a default profile for demo
                    default_user, _ = User.objects.get_or_create(
                        username='demo_user',
                        defaults={
                            'email': 'demo@example.com',
                            'first_name': 'Demo',
                            'last_name': 'User'
                        }
                    )
                    profile, _ = UserProfile.objects.get_or_create(
                        user=default_user,
                        defaults={
                            'height': None,
                            'weight': None,
                            'fitness_level': 'beginner',
                            'goals': ''
                        }
                    )
                
                # Include user data in response
                response_data = UserProfileSerializer(profile).data
                response_data['user'] = {
                    'username': profile.user.username,
                    'first_name': profile.user.first_name,
                    'last_name': profile.user.last_name,
                    'email': profile.user.email
                }
                return Response(response_data)
                
            except Exception as e:
                return Response({
                    'error': f'Database connection failed: {str(e)}',
                    'fallback_data': {
                        'height': None,
                        'weight': None,
                        'fitness_level': 'beginner',
                        'goals': '',
                        'user': {
                            'username': 'demo_user',
                            'first_name': 'Demo',
                            'last_name': 'User',
                            'email': 'demo@example.com'
                        }
                    }
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        elif request.method == 'PUT':
            try:
                # Get or create profile for demo
                profile = UserProfile.objects.first()
                if not profile:
                    default_user, _ = User.objects.get_or_create(
                        username='demo_user',
                        defaults={
                            'email': 'demo@example.com',
                            'first_name': 'Demo',
                            'last_name': 'User'
                        }
                    )
                    profile, _ = UserProfile.objects.get_or_create(user=default_user)
                
                # Handle user data updates if provided
                user_data = request.data.get('user', {})
                if user_data:
                    user_serializer = UserSerializer(profile.user, data=user_data, partial=True)
                    if user_serializer.is_valid():
                        user_serializer.save()
                    else:
                        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
                # Handle profile data updates
                serializer = UserProfileSerializer(profile, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    
                    # Include user data in response
                    response_data = serializer.data
                    response_data['user'] = {
                        'username': profile.user.username,
                        'first_name': profile.user.first_name,
                        'last_name': profile.user.last_name,
                        'email': profile.user.email
                    }
                    return Response(response_data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
            except Exception as e:
                return Response({
                    'error': f'Database save failed: {str(e)}'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    except Exception as e:
        return Response({
            'error': f'Profile operation failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ============ WORKOUT VIEWS ============

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def workout_sessions(request):
    """Get user workout sessions or create new session"""
    if request.method == 'GET':
        sessions = WorkoutSession.objects.filter(user=request.user)
        serializer = WorkoutSessionSerializer(sessions, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = WorkoutSessionSerializer(data=request.data)
        if serializer.is_valid():
            session = serializer.save(user=request.user)
            # Update user workout count
            request.user.update_workout_count()
            return Response(WorkoutSessionSerializer(session).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def workout_analytics(request):
    """Get workout analytics for user"""
    sessions = WorkoutSession.objects.filter(user=request.user)
    
    analytics = {
        'total_workouts': sessions.count(),
        'total_duration': sessions.aggregate(Sum('duration'))['duration__sum'] or 0,
        'average_intensity': sessions.aggregate(Avg('intensity'))['intensity__avg'] or 0,
        'total_calories': sessions.aggregate(Sum('calories_burned'))['calories_burned__sum'] or 0,
        'workout_types': sessions.values('workout_type').annotate(count=Count('id')),
        'recent_sessions': WorkoutSessionSerializer(sessions[:5], many=True).data
    }
    
    return Response(analytics)

# ============ PERFORMANCE VIEWS ============

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def performance_metrics(request):
    """Get or create performance metrics"""
    if request.method == 'GET':
        metrics = PerformanceMetrics.objects.filter(user=request.user)
        serializer = PerformanceMetricsSerializer(metrics, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = PerformanceMetricsSerializer(data=request.data)
        if serializer.is_valid():
            metric = serializer.save(user=request.user)
            return Response(PerformanceMetricsSerializer(metric).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ============ RANKING VIEWS ============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_rankings(request):
    """Get user ranking information"""
    ranking, created = UserRanking.objects.get_or_create(user=request.user)
    serializer = UserRankingSerializer(ranking)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def leaderboard(request):
    """Get leaderboard"""
    rankings = UserRanking.objects.all()[:10]
    serializer = UserRankingSerializer(rankings, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_achievements(request):
    """Get user achievements"""
    achievements = Achievement.objects.filter(user=request.user)
    serializer = AchievementSerializer(achievements, many=True)
    return Response(serializer.data)

# ============ API ROOT VIEW ============

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """API root endpoint"""
    return Response({
        'message': 'Fitness Tracker API',
        'version': '1.0',
        'endpoints': {
            'auth': {
                'register': '/api/register/',
                'login': '/api/login/',
                'logout': '/api/logout/',
                'profile': '/api/profile/',
            },
            'workouts': {
                'sessions': '/api/workouts/',
                'analytics': '/api/analytics/',
            },
            'performance': {
                'metrics': '/api/performance/',
            },
            'rankings': {
                'user': '/api/rankings/',
                'leaderboard': '/api/leaderboard/',
                'achievements': '/api/achievements/',
            }
        }
    })
