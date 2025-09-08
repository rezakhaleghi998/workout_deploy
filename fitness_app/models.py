from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import json

# ============ MAIN USER MODEL ============

class User(AbstractUser):
    """Extended User model for fitness tracking"""
    
    email = models.EmailField(unique=True)
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    fitness_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
            ('expert', 'Expert')
        ],
        default='beginner'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fitness_users'

# ============ WORKOUT MODELS ============

class WorkoutSession(models.Model):
    """Individual workout session tracking"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_sessions')
    workout_type = models.CharField(max_length=100)
    duration_minutes = models.IntegerField()
    calories_burned = models.IntegerField()
    intensity = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('moderate', 'Moderate'),
            ('high', 'High'),
            ('extreme', 'Extreme')
        ],
        default='moderate'
    )
    notes = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'workout_sessions'
        ordering = ['-date']

# ============ ANALYSIS MODELS ============

class WorkoutAnalysis(models.Model):
    """Comprehensive workout analysis data"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_analyses')
    session_date = models.DateTimeField(default=timezone.now)
    
    # Basic workout data
    workout_type = models.CharField(max_length=100)
    duration_minutes = models.IntegerField()
    intensity_level = models.CharField(max_length=20, default='moderate')
    
    # Calculated metrics
    calories_burned = models.FloatField()
    performance_score = models.FloatField(default=0.0)
    
    # Additional data
    notes = models.TextField(blank=True)
    ai_recommendations = models.TextField(blank=True)
    
    class Meta:
        db_table = 'workout_analyses'
        ordering = ['-session_date']

class FitnessPerformanceIndex(models.Model):
    """Performance tracking and indexing"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='performance_indices')
    date = models.DateField(auto_now_add=True)
    
    # Performance metrics
    performance_index = models.FloatField(default=0.0)
    strength_score = models.FloatField(default=0.0)
    endurance_score = models.FloatField(default=0.0)
    flexibility_score = models.FloatField(default=0.0)
    
    # Weekly/Monthly averages
    weekly_avg_calories = models.FloatField(default=0.0)
    monthly_workout_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'performance_indices'
        unique_together = ['user', 'date']

class WellnessPlan(models.Model):
    """AI-generated wellness plans"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wellness_plans')
    plan_name = models.CharField(max_length=200)
    plan_type = models.CharField(
        max_length=50,
        choices=[
            ('weight_loss', 'Weight Loss'),
            ('muscle_gain', 'Muscle Gain'),
            ('endurance', 'Endurance'),
            ('general_fitness', 'General Fitness')
        ],
        default='general_fitness'
    )
    
    # Plan details
    duration_weeks = models.IntegerField(default=4)
    target_calories_per_week = models.IntegerField(default=2000)
    recommended_workouts_per_week = models.IntegerField(default=3)
    
    # AI recommendations
    plan_details = models.TextField()
    nutrition_advice = models.TextField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'wellness_plans'
        ordering = ['-created_at']
