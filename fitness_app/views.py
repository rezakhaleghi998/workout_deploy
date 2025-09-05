from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Q, Sum, Avg, Count
from django.utils import timezone
from datetime import datetime, timedelta

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import (
    User, UserProfile, WorkoutSession, ExerciseType, WorkoutGoal,
    PerformanceMetrics, UserSummaryIndex, FitnessGoal,
    UserRanking, RankingHistory, Achievement
)
from .serializers import (
    UserRegistrationSerializer, UserSerializer, UserProfileSerializer,
    WorkoutSessionSerializer, ExerciseTypeSerializer, WorkoutGoalSerializer,
    PerformanceMetricsSerializer, UserSummaryIndexSerializer, FitnessGoalSerializer,
    UserRankingSerializer, RankingHistorySerializer, AchievementSerializer
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
def register_user(request):
    """Register a new user"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        with transaction.atomic():
            user = serializer.save()
            # Create user profile
            UserProfile.objects.get_or_create(user=user)
            # Create summary index
            UserSummaryIndex.objects.get_or_create(user=user)
            # Create authentication token
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'message': 'User registered successfully',
                'user': UserSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """Authenticate user and return token"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if username and password:
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'Login successful',
                'user': UserSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_200_OK)
    
    return Response({
        'error': 'Invalid credentials'
    }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """Logout user by deleting token"""
    try:
        request.user.auth_token.delete()
        return Response({
            'message': 'Logged out successfully'
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'error': 'Error logging out'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get or update user profile"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'GET':
        user_data = UserSerializer(request.user).data
        profile_data = UserProfileSerializer(profile).data
        return Response({
            'user': user_data,
            'profile': profile_data
        })
    
    elif request.method == 'PUT':
        # Update user data
        user_serializer = UserSerializer(request.user, data=request.data.get('user', {}), partial=True)
        profile_serializer = UserProfileSerializer(profile, data=request.data.get('profile', {}), partial=True)
        
        if user_serializer.is_valid() and profile_serializer.is_valid():
            user_serializer.save()
            profile_serializer.save()
            return Response({
                'message': 'Profile updated successfully',
                'user': user_serializer.data,
                'profile': profile_serializer.data
            })
        
        errors = {}
        if not user_serializer.is_valid():
            errors['user'] = user_serializer.errors
        if not profile_serializer.is_valid():
            errors['profile'] = profile_serializer.errors
        
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

# ============ WORKOUT VIEWS ============

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def workout_sessions(request):
    """Get user's workout sessions or create new session"""
    
    if request.method == 'GET':
        sessions = WorkoutSession.objects.filter(user=request.user).order_by('-date')
        
        # Apply date filtering if provided
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        if start_date:
            sessions = sessions.filter(date__gte=start_date)
        if end_date:
            sessions = sessions.filter(date__lte=end_date)
        
        # Apply pagination
        limit = request.GET.get('limit')
        if limit:
            sessions = sessions[:int(limit)]
        
        serializer = WorkoutSessionSerializer(sessions, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = WorkoutSessionSerializer(data=request.data)
        if serializer.is_valid():
            workout_session = serializer.save(user=request.user)
            
            # Update user's performance metrics
            update_user_performance_metrics(request.user, workout_session)
            
            return Response({
                'message': 'Workout session created successfully',
                'session': WorkoutSessionSerializer(workout_session).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exercise_types(request):
    """Get all available exercise types"""
    exercises = ExerciseType.objects.all().order_by('name')
    serializer = ExerciseTypeSerializer(exercises, many=True)
    return Response(serializer.data)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def workout_goals(request):
    """Get user's workout goals or create new goal"""
    
    if request.method == 'GET':
        goals = WorkoutGoal.objects.filter(user=request.user).order_by('-created_at')
        serializer = WorkoutGoalSerializer(goals, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = WorkoutGoalSerializer(data=request.data)
        if serializer.is_valid():
            goal = serializer.save(user=request.user)
            return Response({
                'message': 'Workout goal created successfully',
                'goal': WorkoutGoalSerializer(goal).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ============ PERFORMANCE VIEWS ============

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def performance_metrics(request):
    """Get user's performance metrics or create/update metrics"""
    
    if request.method == 'GET':
        metrics = PerformanceMetrics.objects.filter(user=request.user).order_by('-date')
        
        # Get specific date if provided
        date = request.GET.get('date')
        if date:
            metrics = metrics.filter(date=date)
        
        # Apply limit
        limit = request.GET.get('limit', 30)
        metrics = metrics[:int(limit)]
        
        serializer = PerformanceMetricsSerializer(metrics, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Get or create metrics for today
        today = timezone.now().date()
        metrics, created = PerformanceMetrics.objects.get_or_create(
            user=request.user,
            date=today,
            defaults=request.data
        )
        
        if not created:
            # Update existing metrics
            serializer = PerformanceMetricsSerializer(metrics, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'message': 'Performance metrics updated successfully',
                    'metrics': serializer.data
                })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = PerformanceMetricsSerializer(metrics)
            return Response({
                'message': 'Performance metrics created successfully',
                'metrics': serializer.data
            }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_summary_index(request):
    """Get user's summary index with advanced analytics"""
    summary, created = UserSummaryIndex.objects.get_or_create(user=request.user)
    
    if created or request.GET.get('refresh') == 'true':
        # Calculate and update summary index
        update_user_summary_index(request.user, summary)
    
    serializer = UserSummaryIndexSerializer(summary)
    return Response(serializer.data)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def fitness_goals(request):
    """Get user's fitness goals or create new goal"""
    
    if request.method == 'GET':
        goals = FitnessGoal.objects.filter(user=request.user).order_by('-created_at')
        status_filter = request.GET.get('status')
        if status_filter:
            goals = goals.filter(status=status_filter)
        
        serializer = FitnessGoalSerializer(goals, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = FitnessGoalSerializer(data=request.data)
        if serializer.is_valid():
            goal = serializer.save(user=request.user)
            return Response({
                'message': 'Fitness goal created successfully',
                'goal': FitnessGoalSerializer(goal).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ============ RANKING VIEWS ============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_rankings(request):
    """Get user's current rankings"""
    rankings = UserRanking.objects.filter(user=request.user).order_by('-created_at')
    
    ranking_type = request.GET.get('type')
    if ranking_type:
        rankings = rankings.filter(ranking_type=ranking_type)
    
    serializer = UserRankingSerializer(rankings, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def leaderboard(request):
    """Get leaderboard for specific ranking type"""
    ranking_type = request.GET.get('type', 'overall')
    limit = int(request.GET.get('limit', 50))
    
    # Get latest rankings for the specified type
    latest_period = UserRanking.objects.filter(
        ranking_type=ranking_type
    ).order_by('-period_end').first()
    
    if not latest_period:
        return Response({'rankings': []})
    
    rankings = UserRanking.objects.filter(
        ranking_type=ranking_type,
        period_start=latest_period.period_start,
        period_end=latest_period.period_end
    ).order_by('rank')[:limit]
    
    serializer = UserRankingSerializer(rankings, many=True)
    return Response({
        'rankings': serializer.data,
        'period_start': latest_period.period_start,
        'period_end': latest_period.period_end,
        'total_participants': latest_period.total_participants
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_achievements(request):
    """Get user's achievements"""
    achievements = Achievement.objects.filter(user=request.user).order_by('-earned_at')
    
    achievement_type = request.GET.get('type')
    if achievement_type:
        achievements = achievements.filter(achievement_type=achievement_type)
    
    serializer = AchievementSerializer(achievements, many=True)
    return Response(serializer.data)

# ============ ANALYTICS VIEWS ============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def workout_analytics(request):
    """Get user's workout analytics and statistics"""
    user = request.user
    
    # Date range
    days = int(request.GET.get('days', 30))
    start_date = timezone.now().date() - timedelta(days=days)
    
    # Get workout sessions in date range
    sessions = WorkoutSession.objects.filter(
        user=user,
        date__gte=start_date
    )
    
    # Calculate statistics
    total_sessions = sessions.count()
    total_calories = sessions.aggregate(Sum('calories_burned'))['calories_burned__sum'] or 0
    total_time = sessions.aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0
    avg_calories_per_session = sessions.aggregate(Avg('calories_burned'))['calories_burned__avg'] or 0
    avg_duration = sessions.aggregate(Avg('duration_minutes'))['duration_minutes__avg'] or 0
    
    # Exercise type breakdown
    exercise_breakdown = sessions.values(
        'exercise_type__name'
    ).annotate(
        count=Count('id'),
        total_calories=Sum('calories_burned'),
        total_time=Sum('duration_minutes')
    ).order_by('-total_calories')
    
    # Weekly trend
    weekly_data = []
    for i in range(4):  # Last 4 weeks
        week_start = start_date + timedelta(weeks=i)
        week_end = week_start + timedelta(days=6)
        week_sessions = sessions.filter(date__range=[week_start, week_end])
        week_calories = week_sessions.aggregate(Sum('calories_burned'))['calories_burned__sum'] or 0
        week_count = week_sessions.count()
        
        weekly_data.append({
            'week': f"Week {i+1}",
            'start_date': week_start,
            'end_date': week_end,
            'sessions': week_count,
            'calories': week_calories
        })
    
    return Response({
        'period_days': days,
        'start_date': start_date,
        'end_date': timezone.now().date(),
        'total_sessions': total_sessions,
        'total_calories': total_calories,
        'total_time_minutes': total_time,
        'avg_calories_per_session': round(avg_calories_per_session, 2),
        'avg_duration_minutes': round(avg_duration, 2),
        'exercise_breakdown': list(exercise_breakdown),
        'weekly_trend': weekly_data
    })

# ============ HELPER FUNCTIONS ============

def update_user_performance_metrics(user, workout_session):
    """Update user's performance metrics after a workout"""
    today = timezone.now().date()
    metrics, created = PerformanceMetrics.objects.get_or_create(
        user=user,
        date=today
    )
    
    # Update totals
    metrics.total_calories_burned += workout_session.calories_burned
    metrics.total_workout_time += workout_session.duration_minutes
    
    # Calculate efficiency
    if metrics.total_workout_time > 0:
        metrics.calorie_efficiency = metrics.total_calories_burned / metrics.total_workout_time
    
    # Update workout frequency (approximate)
    recent_sessions = WorkoutSession.objects.filter(
        user=user,
        date__gte=today - timedelta(days=7)
    ).count()
    metrics.workout_frequency = recent_sessions
    
    # Simple fitness score updates based on workout intensity
    intensity_multiplier = {
        'Low': 0.5,
        'Medium': 1.0,
        'High': 1.5
    }.get(workout_session.intensity, 1.0)
    
    # Update component scores (simplified algorithm)
    if 'cardio' in workout_session.exercise_type.name.lower():
        metrics.cardiovascular_score = min(100, metrics.cardiovascular_score + (2 * intensity_multiplier))
        metrics.endurance_score = min(100, metrics.endurance_score + (1.5 * intensity_multiplier))
    elif 'strength' in workout_session.exercise_type.name.lower():
        metrics.strength_score = min(100, metrics.strength_score + (2 * intensity_multiplier))
    elif 'yoga' in workout_session.exercise_type.name.lower():
        metrics.flexibility_score = min(100, metrics.flexibility_score + (2 * intensity_multiplier))
    
    metrics.save()

def update_user_summary_index(user, summary):
    """Update user's summary index with latest data"""
    # Get all workout sessions
    all_sessions = WorkoutSession.objects.filter(user=user)
    recent_sessions = all_sessions.filter(
        date__gte=timezone.now().date() - timedelta(days=30)
    )
    
    # Basic statistics
    summary.total_sessions = all_sessions.count()
    summary.total_calories = all_sessions.aggregate(
        Sum('calories_burned')
    )['calories_burned__sum'] or 0
    
    if summary.total_sessions > 0:
        summary.average_session_duration = all_sessions.aggregate(
            Avg('duration_minutes')
        )['duration_minutes__avg'] or 0
    
    # Weekly average (last 4 weeks)
    if recent_sessions.exists():
        weekly_calories = recent_sessions.aggregate(
            Sum('calories_burned')
        )['calories_burned__sum'] or 0
        summary.weekly_average_calories = weekly_calories / 4
    
    # Get latest performance metrics
    latest_metrics = PerformanceMetrics.objects.filter(user=user).order_by('-date').first()
    if latest_metrics:
        summary.performance_index = latest_metrics.overall_fitness_index
        summary.efficiency_score = latest_metrics.calorie_efficiency
        
        # Calculate consistency (workouts per week over last month)
        weeks_with_workouts = recent_sessions.dates('date', 'week').count()
        summary.consistency_rating = min(100, (weeks_with_workouts / 4) * 100)
        
        # Simple improvement trend (compare last week vs previous week)
        last_week_start = timezone.now().date() - timedelta(days=7)
        prev_week_start = last_week_start - timedelta(days=7)
        
        last_week_calories = all_sessions.filter(
            date__gte=last_week_start
        ).aggregate(Sum('calories_burned'))['calories_burned__sum'] or 0
        
        prev_week_calories = all_sessions.filter(
            date__gte=prev_week_start,
            date__lt=last_week_start
        ).aggregate(Sum('calories_burned'))['calories_burned__sum'] or 0
        
        if prev_week_calories > 0:
            summary.improvement_trend = ((last_week_calories - prev_week_calories) / prev_week_calories) * 100
        
    summary.save()
