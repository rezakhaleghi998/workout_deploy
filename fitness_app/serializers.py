from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import (
    User, UserProfile, WorkoutSession, ExerciseType, WorkoutGoal,
    PerformanceMetrics, UserSummaryIndex, FitnessGoal,
    UserRanking, RankingHistory, Achievement
)

# ============ USER SERIALIZERS ============

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'total_workouts', 'created_at']
        read_only_fields = ['id', 'total_workouts', 'created_at']

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    bmi = serializers.FloatField(read_only=True)
    bmr = serializers.FloatField(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'age', 'weight', 'height', 'gender', 'fitness_level',
            'bmi', 'bmr', 'created_at', 'updated_at'
        ]
        read_only_fields = ['bmi', 'bmr', 'created_at', 'updated_at']

# ============ WORKOUT SERIALIZERS ============

class ExerciseTypeSerializer(serializers.ModelSerializer):
    """Serializer for exercise types"""
    
    class Meta:
        model = ExerciseType
        fields = ['id', 'name', 'calories_per_hour', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']

class WorkoutGoalSerializer(serializers.ModelSerializer):
    """Serializer for workout goals"""
    goal_type_display = serializers.CharField(source='get_goal_type_display', read_only=True)

    class Meta:
        model = WorkoutGoal
        fields = [
            'id', 'goal_type', 'goal_type_display', 'target_calories_per_week',
            'target_workouts_per_week', 'description', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class WorkoutSessionSerializer(serializers.ModelSerializer):
    """Serializer for workout sessions"""
    exercise_type_name = serializers.CharField(source='exercise_type.name', read_only=True)
    intensity_display = serializers.CharField(source='get_intensity_display', read_only=True)

    class Meta:
        model = WorkoutSession
        fields = [
            'id', 'exercise_type', 'exercise_type_name', 'duration_minutes',
            'calories_burned', 'intensity', 'intensity_display', 'notes',
            'date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_exercise_type(self, value):
        """Ensure exercise type exists"""
        if not ExerciseType.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Invalid exercise type")
        return value

# ============ PERFORMANCE SERIALIZERS ============

class PerformanceMetricsSerializer(serializers.ModelSerializer):
    """Serializer for performance metrics"""
    fitness_grade = serializers.CharField(source='get_fitness_grade', read_only=True)

    class Meta:
        model = PerformanceMetrics
        fields = [
            'id', 'cardiovascular_score', 'strength_score', 'flexibility_score',
            'endurance_score', 'overall_fitness_index', 'fitness_grade',
            'total_calories_burned', 'total_workout_time', 'workout_frequency',
            'calorie_efficiency', 'consistency_score', 'date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'overall_fitness_index', 'created_at', 'updated_at']

class UserSummaryIndexSerializer(serializers.ModelSerializer):
    """Serializer for user summary index"""

    class Meta:
        model = UserSummaryIndex
        fields = [
            'performance_index', 'efficiency_score', 'consistency_rating',
            'improvement_trend', 'total_sessions', 'average_session_duration',
            'total_calories', 'weekly_average_calories', 'global_rank',
            'percentile', 'last_calculated'
        ]
        read_only_fields = ['last_calculated']

class FitnessGoalSerializer(serializers.ModelSerializer):
    """Serializer for fitness goals"""
    progress_percentage = serializers.FloatField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = FitnessGoal
        fields = [
            'id', 'title', 'description', 'target_value', 'current_value',
            'unit', 'target_date', 'status', 'status_display',
            'progress_percentage', 'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = ['id', 'progress_percentage', 'created_at', 'updated_at']

# ============ RANKING SERIALIZERS ============

class UserRankingSerializer(serializers.ModelSerializer):
    """Serializer for user rankings"""
    ranking_type_display = serializers.CharField(source='get_ranking_type_display', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = UserRanking
        fields = [
            'id', 'user', 'username', 'user_full_name', 'ranking_type',
            'ranking_type_display', 'rank', 'score', 'percentile',
            'total_participants', 'points_earned', 'period_start',
            'period_end', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class RankingHistorySerializer(serializers.ModelSerializer):
    """Serializer for ranking history"""
    ranking_type_display = serializers.CharField(source='get_ranking_type_display', read_only=True)
    rank_change_direction = serializers.SerializerMethodField()

    class Meta:
        model = RankingHistory
        fields = [
            'id', 'ranking_type', 'ranking_type_display', 'previous_rank',
            'current_rank', 'rank_change', 'rank_change_direction',
            'previous_score', 'current_score', 'score_change', 'date',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_rank_change_direction(self, obj):
        """Get direction of rank change"""
        if obj.rank_change > 0:
            return 'up'
        elif obj.rank_change < 0:
            return 'down'
        else:
            return 'same'

class AchievementSerializer(serializers.ModelSerializer):
    """Serializer for achievements"""
    achievement_type_display = serializers.CharField(source='get_achievement_type_display', read_only=True)
    rarity_display = serializers.CharField(source='get_rarity_display', read_only=True)

    class Meta:
        model = Achievement
        fields = [
            'id', 'title', 'description', 'achievement_type',
            'achievement_type_display', 'points', 'icon', 'rarity',
            'rarity_display', 'earned_at'
        ]
        read_only_fields = ['id', 'earned_at']

# ============ SPECIALIZED SERIALIZERS ============

class LeaderboardSerializer(serializers.ModelSerializer):
    """Specialized serializer for leaderboard display"""
    username = serializers.CharField(source='user.username')
    full_name = serializers.CharField(source='user.get_full_name')
    user_id = serializers.IntegerField(source='user.id')

    class Meta:
        model = UserRanking
        fields = [
            'rank', 'user_id', 'username', 'full_name', 'score',
            'percentile', 'points_earned'
        ]

class WorkoutStatsSerializer(serializers.Serializer):
    """Serializer for workout statistics"""
    total_sessions = serializers.IntegerField()
    total_calories = serializers.FloatField()
    total_time_minutes = serializers.IntegerField()
    avg_calories_per_session = serializers.FloatField()
    avg_duration_minutes = serializers.FloatField()
    period_days = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()

class ExerciseBreakdownSerializer(serializers.Serializer):
    """Serializer for exercise type breakdown"""
    exercise_type__name = serializers.CharField()
    count = serializers.IntegerField()
    total_calories = serializers.FloatField()
    total_time = serializers.IntegerField()

class WeeklyTrendSerializer(serializers.Serializer):
    """Serializer for weekly trend data"""
    week = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    sessions = serializers.IntegerField()
    calories = serializers.FloatField()

class UserDashboardSerializer(serializers.Serializer):
    """Comprehensive serializer for user dashboard data"""
    user = UserSerializer()
    profile = UserProfileSerializer()
    summary_index = UserSummaryIndexSerializer()
    recent_workouts = WorkoutSessionSerializer(many=True)
    active_goals = FitnessGoalSerializer(many=True)
    current_rankings = UserRankingSerializer(many=True)
    recent_achievements = AchievementSerializer(many=True)

# ============ VALIDATION MIXINS ============

class WorkoutValidationMixin:
    """Mixin for workout-related validation"""
    
    def validate_duration_minutes(self, value):
        """Validate workout duration"""
        if value < 1:
            raise serializers.ValidationError("Duration must be at least 1 minute")
        if value > 480:  # 8 hours
            raise serializers.ValidationError("Duration cannot exceed 8 hours")
        return value
    
    def validate_calories_burned(self, value):
        """Validate calories burned"""
        if value < 1:
            raise serializers.ValidationError("Calories burned must be positive")
        if value > 2000:
            raise serializers.ValidationError("Calories burned seems too high for a single session")
        return value

class ProfileValidationMixin:
    """Mixin for profile-related validation"""
    
    def validate_age(self, value):
        """Validate age"""
        if value and (value < 13 or value > 120):
            raise serializers.ValidationError("Age must be between 13 and 120")
        return value
    
    def validate_weight(self, value):
        """Validate weight"""
        if value and (value < 30 or value > 300):
            raise serializers.ValidationError("Weight must be between 30 and 300 kg")
        return value
    
    def validate_height(self, value):
        """Validate height"""
        if value and (value < 100 or value > 250):
            raise serializers.ValidationError("Height must be between 100 and 250 cm")
        return value

# Apply mixins to relevant serializers
WorkoutSessionSerializer.__bases__ = (WorkoutValidationMixin, serializers.ModelSerializer)
UserProfileSerializer.__bases__ = (ProfileValidationMixin, serializers.ModelSerializer)
