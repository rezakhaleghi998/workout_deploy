from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import json

# ============ USER MODELS ============

class User(AbstractUser):
    """Extended User model with fitness tracking capabilities"""

    email = models.EmailField(unique=True)
    total_workouts = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    # Fix the reverse accessor conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='fitness_users',
        related_query_name='fitness_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='fitness_users',
        related_query_name='fitness_user',
    )

    def __str__(self):
        return self.username

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def update_workout_count(self):
        self.total_workouts = self.workout_sessions.count()
        self.save()

class UserProfile(models.Model):
    """Extended profile information for users"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    date_of_birth = models.DateField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True, help_text="Height in cm")
    weight = models.FloatField(null=True, blank=True, help_text="Weight in kg")
    fitness_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
            ('expert', 'Expert'),
        ],
        default='beginner'
    )
    goals = models.TextField(blank=True, help_text="User's fitness goals")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def age(self):
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None

# ============ WORKOUT MODELS ============

class WorkoutSession(models.Model):
    """Individual workout session"""
    
    WORKOUT_TYPES = [
        ('cardio', 'Cardio'),
        ('strength', 'Strength Training'),
        ('flexibility', 'Flexibility'),
        ('sports', 'Sports'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_sessions')
    workout_type = models.CharField(max_length=20, choices=WORKOUT_TYPES)
    date = models.DateTimeField(default=timezone.now)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    intensity = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Intensity level 1-10"
    )
    calories_burned = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username} - {self.workout_type} on {self.date.strftime('%Y-%m-%d')}"

# ============ PERFORMANCE MODELS ============

class PerformanceMetrics(models.Model):
    """Track user performance metrics over time"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='performance_metrics')
    date = models.DateField(default=timezone.now)
    weight = models.FloatField(null=True, blank=True, help_text="Weight in kg")
    body_fat_percentage = models.FloatField(null=True, blank=True)
    muscle_mass = models.FloatField(null=True, blank=True, help_text="Muscle mass in kg")
    cardiovascular_fitness = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    strength_level = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    flexibility_score = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['user', 'date']
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"

# ============ RANKING MODELS ============

class UserRanking(models.Model):
    """User ranking and achievements"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ranking')
    total_points = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    rank = models.PositiveIntegerField(default=0)
    badges = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-total_points']
    
    def __str__(self):
        return f"{self.user.username} - Level {self.level} (Rank #{self.rank})"
    
    def add_points(self, points):
        self.total_points += points
        self.update_level()
        self.save()
    
    def update_level(self):
        # Simple level calculation: every 1000 points = 1 level
        new_level = (self.total_points // 1000) + 1
        if new_level > self.level:
            self.level = new_level
    
    def add_badge(self, badge_name):
        if badge_name not in self.badges:
            self.badges.append(badge_name)
            self.save()

class Achievement(models.Model):
    """Fitness achievements and milestones"""
    
    ACHIEVEMENT_TYPES = [
        ('workout_count', 'Workout Count'),
        ('streak', 'Workout Streak'),
        ('weight_loss', 'Weight Loss'),
        ('endurance', 'Endurance'),
        ('strength', 'Strength'),
        ('consistency', 'Consistency'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    title = models.CharField(max_length=100)
    description = models.TextField()
    points_awarded = models.PositiveIntegerField(default=0)
    achieved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-achieved_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"

# ============ WORKOUT ANALYSIS MODELS (FOR 14-PAGE ANALYSIS) ============

class WorkoutAnalysis(models.Model):
    """Comprehensive workout analysis capturing all 14-page analysis data"""
    
    WORKOUT_TYPES = [
        ('Running', 'Running'),
        ('Cycling', 'Cycling'),
        ('Swimming', 'Swimming'),
        ('Weight Training', 'Weight Training'),
        ('HIIT', 'HIIT'),
        ('Yoga', 'Yoga'),
        ('Walking', 'Walking'),
        ('Boxing', 'Boxing'),
        ('Pilates', 'Pilates'),
        ('CrossFit', 'CrossFit'),
        ('Other', 'Other'),
    ]
    
    MOOD_CHOICES = [
        ('Very Happy', 'Very Happy 😄'),
        ('Happy', 'Happy 😊'),
        ('Neutral', 'Neutral 😐'),
        ('Sad', 'Sad 😢'),
        ('Very Sad', 'Very Sad 😭'),
    ]
    
    INTENSITY_LEVELS = [
        ('Low', 'Low Intensity'),
        ('Medium', 'Medium Intensity'),
        ('High', 'High Intensity'),
    ]
    
    ACTIVITY_LEVELS = [
        ('Sedentary', 'Sedentary'),
        ('Lightly Active', 'Lightly Active'),
        ('Moderately Active', 'Moderately Active'),
        ('Very Active', 'Very Active'),
        ('Super Active', 'Super Active'),
    ]
    
    ANALYSIS_TYPES = [
        ('for_me', 'Analyze for Me'),
        ('for_someone_else', 'Analyze for Someone Else'),
    ]
    
    # Basic info
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_analyses')
    analysis_type = models.CharField(max_length=20, choices=ANALYSIS_TYPES, default='for_me')
    
    # Form data (from the app's input form)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    height_cm = models.DecimalField(max_digits=5, decimal_places=2)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2)
    workout_type = models.CharField(max_length=50, choices=WORKOUT_TYPES)
    duration_minutes = models.IntegerField()
    heart_rate_bpm = models.IntegerField(null=True, blank=True)
    distance_km = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    sleep_hours = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_LEVELS)
    mood_before = models.CharField(max_length=20, choices=MOOD_CHOICES, null=True, blank=True)
    
    # Results (from the 14-page analysis)
    predicted_calories = models.DecimalField(max_digits=7, decimal_places=2)
    calories_per_minute = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    calorie_range_min = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    calorie_range_max = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    burn_efficiency = models.CharField(max_length=20, null=True, blank=True)
    intensity_level = models.CharField(max_length=10, choices=INTENSITY_LEVELS, null=True, blank=True)
    efficiency_grade = models.CharField(max_length=5, null=True, blank=True)  # B+, A-, etc.
    
    # Fitness Performance Index data
    fitness_performance_index = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    consistency_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    performance_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    variety_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    intensity_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # User rankings
    user_ranking_overall = models.IntegerField(null=True, blank=True)
    user_ranking_fitness = models.IntegerField(null=True, blank=True)
    user_ranking_consistency = models.IntegerField(null=True, blank=True)
    percentile_rank = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    total_users_in_comparison = models.IntegerField(null=True, blank=True)
    
    # Pace and distance
    average_pace_min_per_km = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    speed_kmh = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    calories_per_km = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    # Mood prediction
    predicted_mood_after = models.CharField(max_length=20, choices=MOOD_CHOICES, null=True, blank=True)
    mood_improvement_levels = models.IntegerField(null=True, blank=True)
    
    # AI recommendations (store as JSON)
    ai_diet_recommendations = models.JSONField(null=True, blank=True)
    ai_workout_recommendations = models.JSONField(null=True, blank=True)
    ai_sleep_recommendations = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Workout Analysis"
        verbose_name_plural = "Workout Analyses"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.workout_type} - {self.predicted_calories} cal ({self.created_at.strftime('%Y-%m-%d')})"

class FitnessPerformanceIndex(models.Model):
    """Detailed Fitness Performance Index tracking"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fitness_performance')
    workout_analysis = models.OneToOneField(WorkoutAnalysis, on_delete=models.CASCADE, null=True, blank=True)
    
    # Main performance index
    overall_score = models.DecimalField(max_digits=5, decimal_places=2)
    fitness_level = models.CharField(max_length=20)  # Beginner, Intermediate, Advanced
    progress_status = models.CharField(max_length=50)  # Building momentum, Steady progress
    
    # Individual metrics (from the purple panel)
    consistency_score = models.DecimalField(max_digits=5, decimal_places=2)
    consistency_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    performance_score = models.DecimalField(max_digits=5, decimal_places=2)
    performance_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    variety_score = models.DecimalField(max_digits=5, decimal_places=2)
    variety_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    intensity_score = models.DecimalField(max_digits=5, decimal_places=2)
    intensity_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Progress tracking
    weekly_change = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    weekly_change_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    monthly_change = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    monthly_change_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Performance insights
    insights = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Fitness Performance Index"
        verbose_name_plural = "Fitness Performance Indices"
        ordering = ['-created_at']

class WellnessPlan(models.Model):
    """AI-generated wellness plans from the analysis"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wellness_plans')
    workout_analysis = models.ForeignKey(WorkoutAnalysis, on_delete=models.CASCADE, null=True, blank=True)
    
    # Caloric data (from Section 3.1 of the analysis)
    total_daily_calories_needed = models.DecimalField(max_digits=7, decimal_places=2)
    basal_metabolic_rate = models.DecimalField(max_digits=7, decimal_places=2)
    activity_calories = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    workout_calories = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    recommended_intake = models.DecimalField(max_digits=7, decimal_places=2)
    
    # AI recommendations (from Section 3.3)
    personalized_diet_plan = models.JSONField(null=True, blank=True)
    advanced_workout_programming = models.JSONField(null=True, blank=True)
    sleep_recovery_optimization = models.JSONField(null=True, blank=True)
    supplement_recommendations = models.JSONField(null=True, blank=True)
    progress_tracking_guidelines = models.JSONField(null=True, blank=True)
    lifestyle_integration = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Wellness Plan"
        verbose_name_plural = "Wellness Plans"
        ordering = ['-created_at']
