from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import json

# ============ RAILWAY-OPTIMIZED USER MODELS ============

class User(AbstractUser):
    """Railway-optimized User model with fitness tracking capabilities"""

    email = models.EmailField(unique=True, db_index=True)
    height = models.FloatField(
        null=True, 
        blank=True, 
        validators=[MinValueValidator(50), MaxValueValidator(300)],
        help_text="Height in centimeters"
    )
    weight = models.FloatField(
        null=True, 
        blank=True, 
        validators=[MinValueValidator(20), MaxValueValidator(500)],
        help_text="Weight in kilograms"
    )
    age = models.IntegerField(
        null=True, 
        blank=True, 
        validators=[MinValueValidator(13), MaxValueValidator(120)]
    )
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
    total_workouts = models.PositiveIntegerField(default=0)
    total_calories_burned = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    # Fix the reverse accessor conflicts for Railway
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

    class Meta:
        db_table = 'fitness_users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['fitness_level']),
            models.Index(fields=['created_at']),
            models.Index(fields=['username', 'email']),
        ]

    def __str__(self):
        return f"{self.username} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def update_workout_stats(self):
        """Update workout statistics for Railway analytics"""
        workout_sessions = self.workout_sessions.all()
        self.total_workouts = workout_sessions.count()
        self.total_calories_burned = sum(
            session.calories_burned for session in workout_sessions
        )
        self.save(update_fields=['total_workouts', 'total_calories_burned'])

    @property
    def bmi(self):
        """Calculate BMI if height and weight are available"""
        if self.height and self.weight:
            height_m = self.height / 100  # Convert cm to meters
            return round(self.weight / (height_m ** 2), 2)
        return None

    @property
    def fitness_score(self):
        """Calculate overall fitness score for Railway dashboard"""
        if self.total_workouts == 0:
            return 0
        
        # Base score from workout frequency
        base_score = min(self.total_workouts * 2, 50)
        
        # Bonus for consistency (recent activity)
        recent_workouts = self.workout_sessions.filter(
            date__gte=timezone.now() - timezone.timedelta(days=30)
        ).count()
        consistency_bonus = min(recent_workouts * 5, 30)
        
        # Fitness level bonus
        level_bonus = {
            'beginner': 0,
            'intermediate': 10,
            'advanced': 15,
            'expert': 20
        }.get(self.fitness_level, 0)
        
        return min(base_score + consistency_bonus + level_bonus, 100)

class WorkoutSession(models.Model):
    """Railway-optimized workout session tracking"""
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='workout_sessions',
        db_index=True
    )
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    workout_type = models.CharField(max_length=50, db_index=True)
    duration_minutes = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(480)]
    )
    calories_burned = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5000)]
    )
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
    heart_rate_avg = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(60), MaxValueValidator(220)]
    )
    notes = models.TextField(blank=True)
    performance_rating = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Rate your performance (1-10)"
    )

    class Meta:
        db_table = 'workout_sessions'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['workout_type']),
            models.Index(fields=['date']),
            models.Index(fields=['user', 'workout_type']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.workout_type} ({self.date.strftime('%Y-%m-%d')})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update user stats when workout is saved
        self.user.update_workout_stats()

class PerformanceMetric(models.Model):
    """Railway-optimized performance tracking"""
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='performance_metrics',
        db_index=True
    )
    date = models.DateField(auto_now_add=True, db_index=True)
    weight = models.FloatField(
        validators=[MinValueValidator(20), MaxValueValidator(500)]
    )
    body_fat_percentage = models.FloatField(
        null=True, 
        blank=True, 
        validators=[MinValueValidator(3), MaxValueValidator(50)]
    )
    muscle_mass = models.FloatField(
        null=True, 
        blank=True, 
        validators=[MinValueValidator(10), MaxValueValidator(200)]
    )
    performance_index = models.FloatField(
        default=0.0, 
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    resting_heart_rate = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(40), MaxValueValidator(120)]
    )
    blood_pressure_systolic = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(80), MaxValueValidator(200)]
    )
    blood_pressure_diastolic = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(50), MaxValueValidator(120)]
    )

    class Meta:
        db_table = 'performance_metrics'
        unique_together = ['user', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['date']),
            models.Index(fields=['user', 'performance_index']),
        ]

    def __str__(self):
        return f"{self.user.username} - Performance ({self.date})"

    @property
    def bmi(self):
        """Calculate BMI using current weight and user height"""
        if self.user.height and self.weight:
            height_m = self.user.height / 100
            return round(self.weight / (height_m ** 2), 2)
        return None

    def calculate_performance_index(self):
        """Calculate comprehensive performance index for Railway analytics"""
        index = 0
        
        # BMI component (30% of score)
        bmi = self.bmi
        if bmi:
            if 18.5 <= bmi <= 24.9:
                index += 30
            elif 25 <= bmi <= 29.9:
                index += 20
            else:
                index += 10
                
        # Body fat component (25% of score)
        if self.body_fat_percentage:
            if 6 <= self.body_fat_percentage <= 24:
                index += 25
            elif 25 <= self.body_fat_percentage <= 31:
                index += 15
            else:
                index += 5
                
        # Resting heart rate component (20% of score)
        if self.resting_heart_rate:
            if 60 <= self.resting_heart_rate <= 70:
                index += 20
            elif 71 <= self.resting_heart_rate <= 80:
                index += 15
            else:
                index += 10
                
        # Recent workout performance (25% of score)
        recent_workouts = self.user.workout_sessions.filter(
            date__gte=timezone.now() - timezone.timedelta(days=30)
        )
        if recent_workouts.exists():
            avg_rating = recent_workouts.aggregate(
                avg_rating=models.Avg('performance_rating')
            )['avg_rating']
            index += (avg_rating / 10) * 25
            
        self.performance_index = round(index, 2)
        return self.performance_index

class UserProfile(models.Model):
    """Extended profile information for Railway dashboard"""
    
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
