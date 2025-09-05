from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, UserProfile, WorkoutSession, PerformanceMetrics, UserRanking, Achievement

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
    """Serializer for user information"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'total_workouts', 'date_joined']
        read_only_fields = ['id', 'total_workouts', 'date_joined']

# ============ PROFILE SERIALIZERS ============

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    user = UserSerializer(read_only=True)
    age = serializers.ReadOnlyField()

    class Meta:
        model = UserProfile
        fields = ['user', 'date_of_birth', 'height', 'weight', 'fitness_level', 'goals', 'age']

# ============ WORKOUT SERIALIZERS ============

class WorkoutSessionSerializer(serializers.ModelSerializer):
    """Serializer for workout sessions"""
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = WorkoutSession
        fields = ['id', 'user', 'workout_type', 'date', 'duration', 'intensity', 'calories_burned', 'notes']
        read_only_fields = ['id', 'user']

    def validate_duration(self, value):
        if value <= 0:
            raise serializers.ValidationError("Duration must be positive")
        return value

    def validate_intensity(self, value):
        if not 1 <= value <= 10:
            raise serializers.ValidationError("Intensity must be between 1 and 10")
        return value

# ============ PERFORMANCE SERIALIZERS ============

class PerformanceMetricsSerializer(serializers.ModelSerializer):
    """Serializer for performance metrics"""
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = PerformanceMetrics
        fields = ['id', 'user', 'date', 'weight', 'body_fat_percentage', 'muscle_mass', 
                 'cardiovascular_fitness', 'strength_level', 'flexibility_score', 'notes']
        read_only_fields = ['id', 'user']

# ============ RANKING SERIALIZERS ============

class UserRankingSerializer(serializers.ModelSerializer):
    """Serializer for user rankings"""
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserRanking
        fields = ['user', 'total_points', 'level', 'rank', 'badges']
        read_only_fields = ['user', 'rank']

class AchievementSerializer(serializers.ModelSerializer):
    """Serializer for achievements"""
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Achievement
        fields = ['id', 'user', 'achievement_type', 'title', 'description', 'points_awarded', 'achieved_at']
        read_only_fields = ['id', 'user', 'achieved_at']
