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
