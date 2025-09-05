from django.shortcuts import render
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Q, Sum, Avg, Count
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
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
@csrf_exempt
def register_user(request):
    """Register a new user"""
    print(f"Registration attempt - Request data: {request.data}")
    
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        with transaction.atomic():
            user = serializer.save()
            print(f"User created successfully: {user.username} (ID: {user.id})")
            
            # Create user profile
            UserProfile.objects.get_or_create(user=user)
            # Create user ranking
            UserRanking.objects.get_or_create(user=user)
            # Create auth token
            token, created = Token.objects.get_or_create(user=user)
            
            # Test immediate authentication
            test_auth = authenticate(username=user.username, password=request.data.get('password'))
            print(f"Immediate auth test for {user.username}: {test_auth}")
            
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key,
                'message': 'User registered successfully'
            }, status=status.HTTP_201_CREATED)
    else:
        print(f"Registration validation errors: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def login_user(request):
    """Login user and return token"""
    print(f"Login attempt - Request data: {request.data}")
    print(f"Login attempt - Content type: {request.content_type}")
    
    username = request.data.get('username')
    password = request.data.get('password')
    
    print(f"Extracted - Username: {username}, Password: {'*' * len(password) if password else None}")
    
    if username and password:
        user = authenticate(username=username, password=password)
        print(f"Authentication result: {user}")
        
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
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get or update user profile"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        # Handle user data updates if provided
        user_data = request.data.get('user', {})
        if user_data:
            user_serializer = UserSerializer(request.user, data=user_data, partial=True)
            if user_serializer.is_valid():
                user_serializer.save()
            else:
                return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Handle profile data updates
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
