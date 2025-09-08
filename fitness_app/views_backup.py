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

from .models import (
    User, WorkoutSession, WorkoutAnalysis, FitnessPerformanceIndex, WellnessPlan
)
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

# ============ WORKOUT ANALYSIS VIEWS (FOR 14-PAGE ANALYSIS) ============

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_workout_analysis(request):
    """
    Save comprehensive workout analysis data from the 14-page analysis.
    This endpoint captures all the data without changing the user experience.
    """
    try:
        data = request.data
        
        # Create the main workout analysis record
        workout_analysis = WorkoutAnalysis.objects.create(
            user=request.user,
            analysis_type=data.get('analysis_type', 'for_me'),
            
            # Form data
            age=data.get('age'),
            gender=data.get('gender'),
            height_cm=data.get('height_cm'),
            weight_kg=data.get('weight_kg'),
            workout_type=data.get('workout_type'),
            duration_minutes=data.get('duration_minutes'),
            heart_rate_bpm=data.get('heart_rate_bpm'),
            distance_km=data.get('distance_km'),
            sleep_hours=data.get('sleep_hours'),
            activity_level=data.get('activity_level'),
            mood_before=data.get('mood_before'),
            
            # Results
            predicted_calories=data.get('predicted_calories'),
            calories_per_minute=data.get('calories_per_minute'),
            calorie_range_min=data.get('calorie_range_min'),
            calorie_range_max=data.get('calorie_range_max'),
            burn_efficiency=data.get('burn_efficiency'),
            intensity_level=data.get('intensity_level'),
            efficiency_grade=data.get('efficiency_grade'),
            
            # Performance Index
            fitness_performance_index=data.get('fitness_performance_index'),
            consistency_score=data.get('consistency_score'),
            performance_score=data.get('performance_score'),
            variety_score=data.get('variety_score'),
            intensity_score=data.get('intensity_score'),
            
            # Rankings
            user_ranking_overall=data.get('user_ranking_overall'),
            user_ranking_fitness=data.get('user_ranking_fitness'),
            user_ranking_consistency=data.get('user_ranking_consistency'),
            percentile_rank=data.get('percentile_rank'),
            total_users_in_comparison=data.get('total_users_in_comparison'),
            
            # Pace and distance
            average_pace_min_per_km=data.get('average_pace_min_per_km'),
            speed_kmh=data.get('speed_kmh'),
            calories_per_km=data.get('calories_per_km'),
            
            # Mood prediction
            predicted_mood_after=data.get('predicted_mood_after'),
            mood_improvement_levels=data.get('mood_improvement_levels'),
            
            # AI recommendations
            ai_diet_recommendations=data.get('ai_diet_recommendations'),
            ai_workout_recommendations=data.get('ai_workout_recommendations'),
            ai_sleep_recommendations=data.get('ai_sleep_recommendations'),
        )
        
        # Create detailed Fitness Performance Index if data provided
        if data.get('detailed_performance_index'):
            performance_data = data['detailed_performance_index']
            FitnessPerformanceIndex.objects.create(
                user=request.user,
                workout_analysis=workout_analysis,
                overall_score=performance_data.get('overall_score'),
                fitness_level=performance_data.get('fitness_level'),
                progress_status=performance_data.get('progress_status'),
                consistency_score=performance_data.get('consistency_score'),
                consistency_percentage=performance_data.get('consistency_percentage'),
                performance_score=performance_data.get('performance_score'),
                performance_percentage=performance_data.get('performance_percentage'),
                variety_score=performance_data.get('variety_score'),
                variety_percentage=performance_data.get('variety_percentage'),
                intensity_score=performance_data.get('intensity_score'),
                intensity_percentage=performance_data.get('intensity_percentage'),
                weekly_change=performance_data.get('weekly_change'),
                weekly_change_percentage=performance_data.get('weekly_change_percentage'),
                monthly_change=performance_data.get('monthly_change'),
                monthly_change_percentage=performance_data.get('monthly_change_percentage'),
                insights=performance_data.get('insights'),
            )
        
        # Create wellness plan if data provided
        if data.get('wellness_plan'):
            wellness_data = data['wellness_plan']
            WellnessPlan.objects.create(
                user=request.user,
                workout_analysis=workout_analysis,
                total_daily_calories_needed=wellness_data.get('total_daily_calories_needed'),
                basal_metabolic_rate=wellness_data.get('basal_metabolic_rate'),
                activity_calories=wellness_data.get('activity_calories'),
                workout_calories=wellness_data.get('workout_calories'),
                recommended_intake=wellness_data.get('recommended_intake'),
                personalized_diet_plan=wellness_data.get('personalized_diet_plan'),
                advanced_workout_programming=wellness_data.get('advanced_workout_programming'),
                sleep_recovery_optimization=wellness_data.get('sleep_recovery_optimization'),
                supplement_recommendations=wellness_data.get('supplement_recommendations'),
                progress_tracking_guidelines=wellness_data.get('progress_tracking_guidelines'),
                lifestyle_integration=wellness_data.get('lifestyle_integration'),
            )
        
        # Update user profile with latest data
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        if data.get('height_cm'):
            profile.height = data.get('height_cm')
        if data.get('weight_kg'):
            profile.weight = data.get('weight_kg')
        profile.save()
        
        return Response({
            'message': 'Workout analysis saved successfully',
            'analysis_id': workout_analysis.id,
            'user_total_analyses': request.user.workout_analyses.count()
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'Failed to save workout analysis: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_workout_analyses(request):
    """Get user's workout analysis history"""
    try:
        analyses = WorkoutAnalysis.objects.filter(user=request.user).order_by('-created_at')[:10]
        
        data = []
        for analysis in analyses:
            data.append({
                'id': analysis.id,
                'workout_type': analysis.workout_type,
                'predicted_calories': float(analysis.predicted_calories),
                'efficiency_grade': analysis.efficiency_grade,
                'fitness_performance_index': float(analysis.fitness_performance_index) if analysis.fitness_performance_index else None,
                'duration_minutes': analysis.duration_minutes,
                'created_at': analysis.created_at.isoformat(),
                'percentile_rank': float(analysis.percentile_rank) if analysis.percentile_rank else None,
            })
        
        return Response({
            'total_analyses': request.user.workout_analyses.count(),
            'recent_analyses': data
        })
        
    except Exception as e:
        return Response({
            'error': f'Failed to retrieve analyses: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_performance_analytics(request):
    """Get user's performance analytics dashboard data"""
    try:
        analyses = WorkoutAnalysis.objects.filter(user=request.user)
        
        if not analyses.exists():
            return Response({
                'message': 'No workout analyses found',
                'analytics': {}
            })
        
        # Calculate analytics
        total_analyses = analyses.count()
        avg_calories = analyses.aggregate(avg=Avg('predicted_calories'))['avg']
        avg_performance_index = analyses.aggregate(avg=Avg('fitness_performance_index'))['avg']
        
        # Workout type distribution
        workout_types = {}
        for analysis in analyses:
            workout_type = analysis.workout_type
            if workout_type not in workout_types:
                workout_types[workout_type] = 0
            workout_types[workout_type] += 1
        
        # Recent performance trend
        recent_analyses = analyses.order_by('-created_at')[:5]
        performance_trend = []
        for analysis in recent_analyses:
            performance_trend.append({
                'date': analysis.created_at.strftime('%Y-%m-%d'),
                'performance_index': float(analysis.fitness_performance_index) if analysis.fitness_performance_index else 0,
                'calories': float(analysis.predicted_calories)
            })
        
        return Response({
            'analytics': {
                'total_analyses': total_analyses,
                'average_calories': round(avg_calories, 2) if avg_calories else 0,
                'average_performance_index': round(avg_performance_index, 2) if avg_performance_index else 0,
                'workout_type_distribution': workout_types,
                'performance_trend': list(reversed(performance_trend))  # Oldest to newest
            }
        })
        
    except Exception as e:
        return Response({
            'error': f'Failed to retrieve analytics: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)
