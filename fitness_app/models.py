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
    
    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.username
    
    def get_full_name(self):
        """Return the user's full name"""
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    def increment_workout_count(self):
        """Increment total workout count"""
        self.total_workouts += 1
        self.save(update_fields=['total_workouts'])

class UserProfile(models.Model):
    """User profile with fitness-related information"""
    
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    
    FITNESS_LEVEL_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        ('Expert', 'Expert'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Physical characteristics
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(13), MaxValueValidator(120)],
        null=True, blank=True,
        help_text="Age in years"
    )
    weight = models.FloatField(
        validators=[MinValueValidator(30.0), MaxValueValidator(300.0)],
        null=True, blank=True,
        help_text="Weight in kg"
    )
    height = models.FloatField(
        validators=[MinValueValidator(100.0), MaxValueValidator(250.0)],
        null=True, blank=True,
        help_text="Height in cm"
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    
    # Fitness information
    fitness_level = models.CharField(
        max_length=15, 
        choices=FITNESS_LEVEL_CHOICES, 
        default='Beginner'
    )
    
    # Calculated fields
    bmi = models.FloatField(null=True, blank=True, help_text="Body Mass Index")
    bmr = models.FloatField(null=True, blank=True, help_text="Basal Metabolic Rate")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def calculate_bmi(self):
        """Calculate BMI if height and weight are available"""
        if self.height and self.weight:
            height_m = self.height / 100  # Convert cm to meters
            self.bmi = self.weight / (height_m ** 2)
            return self.bmi
        return None
    
    def calculate_bmr(self):
        """Calculate BMR using Mifflin-St Jeor Equation"""
        if self.weight and self.height and self.age and self.gender:
            if self.gender == 'Male':
                self.bmr = (10 * self.weight) + (6.25 * self.height) - (5 * self.age) + 5
            else:  # Female or Other
                self.bmr = (10 * self.weight) + (6.25 * self.height) - (5 * self.age) - 161
            return self.bmr
        return None
    
    def save(self, *args, **kwargs):
        """Auto-calculate BMI and BMR on save"""
        self.calculate_bmi()
        self.calculate_bmr()
        super().save(*args, **kwargs)

# ============ WORKOUT MODELS ============

class ExerciseType(models.Model):
    """Predefined exercise types with calorie data"""
    
    name = models.CharField(max_length=100, unique=True)
    calories_per_hour = models.FloatField(
        validators=[MinValueValidator(50.0), MaxValueValidator(2000.0)],
        help_text="Average calories burned per hour"
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Exercise Type'
        verbose_name_plural = 'Exercise Types'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.calories_per_hour} cal/hr)"

class WorkoutGoal(models.Model):
    """User's workout goals"""
    
    GOAL_TYPE_CHOICES = [
        ('weight_loss', 'Weight Loss'),
        ('muscle_gain', 'Muscle Gain'),
        ('endurance', 'Endurance'),
        ('strength', 'Strength'),
        ('general_fitness', 'General Fitness'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_goals')
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPE_CHOICES)
    target_calories_per_week = models.PositiveIntegerField(
        validators=[MinValueValidator(500), MaxValueValidator(10000)],
        help_text="Target calories to burn per week"
    )
    target_workouts_per_week = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(14)],
        default=3
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Workout Goal'
        verbose_name_plural = 'Workout Goals'
        unique_together = ['user', 'goal_type', 'is_active']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_goal_type_display()}"

class WorkoutSession(models.Model):
    """Individual workout sessions"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_sessions')
    exercise_type = models.ForeignKey(
        ExerciseType, 
        on_delete=models.CASCADE, 
        related_name='workout_sessions'
    )
    
    # Workout details
    duration_minutes = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(480)],
        help_text="Duration in minutes"
    )
    calories_burned = models.FloatField(
        validators=[MinValueValidator(1.0), MaxValueValidator(2000.0)],
        help_text="Calories burned during workout"
    )
    intensity = models.CharField(
        max_length=10,
        choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')],
        default='Medium'
    )
    
    # Session metadata
    notes = models.TextField(blank=True)
    date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Workout Session'
        verbose_name_plural = 'Workout Sessions'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username} - {self.exercise_type.name} ({self.date.date()})"
    
    def save(self, *args, **kwargs):
        """Auto-increment user workout count on creation"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.user.increment_workout_count()

# ============ PERFORMANCE MODELS ============

class PerformanceMetrics(models.Model):
    """User performance metrics and fitness tracking"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='performance_metrics')
    
    # Fitness Index Components
    cardiovascular_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        default=50.0,
        help_text="Cardiovascular fitness score (0-100)"
    )
    strength_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        default=50.0,
        help_text="Strength fitness score (0-100)"
    )
    flexibility_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        default=50.0,
        help_text="Flexibility score (0-100)"
    )
    endurance_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        default=50.0,
        help_text="Endurance score (0-100)"
    )
    
    # Calculated overall score
    overall_fitness_index = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        default=50.0,
        help_text="Overall fitness index (0-100)"
    )
    
    # Performance tracking
    total_calories_burned = models.FloatField(default=0.0)
    total_workout_time = models.PositiveIntegerField(default=0, help_text="Total minutes")
    workout_frequency = models.FloatField(default=0.0, help_text="Workouts per week")
    
    # Efficiency metrics
    calorie_efficiency = models.FloatField(
        default=0.0,
        help_text="Calories burned per minute"
    )
    consistency_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        default=0.0,
        help_text="Workout consistency score"
    )
    
    # Timestamps
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Performance Metrics'
        verbose_name_plural = 'Performance Metrics'
        unique_together = ['user', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username} - {self.date} (Index: {self.overall_fitness_index:.1f})"
    
    def calculate_overall_fitness_index(self):
        """Calculate overall fitness index from component scores"""
        self.overall_fitness_index = (
            self.cardiovascular_score * 0.3 +
            self.strength_score * 0.25 +
            self.flexibility_score * 0.2 +
            self.endurance_score * 0.25
        )
        return self.overall_fitness_index
    
    def get_fitness_grade(self):
        """Get letter grade based on fitness index"""
        if self.overall_fitness_index >= 90:
            return 'A+'
        elif self.overall_fitness_index >= 85:
            return 'A'
        elif self.overall_fitness_index >= 80:
            return 'A-'
        elif self.overall_fitness_index >= 75:
            return 'B+'
        elif self.overall_fitness_index >= 70:
            return 'B'
        elif self.overall_fitness_index >= 65:
            return 'B-'
        elif self.overall_fitness_index >= 60:
            return 'C+'
        elif self.overall_fitness_index >= 55:
            return 'C'
        elif self.overall_fitness_index >= 50:
            return 'C-'
        else:
            return 'D'
    
    def save(self, *args, **kwargs):
        """Auto-calculate overall fitness index on save"""
        self.calculate_overall_fitness_index()
        super().save(*args, **kwargs)

class UserSummaryIndex(models.Model):
    """User summary index with advanced analytics"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='summary_index')
    
    # Performance Index
    performance_index = models.FloatField(default=0.0)
    efficiency_score = models.FloatField(default=0.0)
    consistency_rating = models.FloatField(default=0.0)
    improvement_trend = models.FloatField(default=0.0)
    
    # Activity Statistics
    total_sessions = models.PositiveIntegerField(default=0)
    average_session_duration = models.FloatField(default=0.0)
    total_calories = models.FloatField(default=0.0)
    weekly_average_calories = models.FloatField(default=0.0)
    
    # Rankings
    global_rank = models.PositiveIntegerField(null=True, blank=True)
    percentile = models.FloatField(null=True, blank=True)
    
    # Metadata
    last_calculated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Summary Index'
        verbose_name_plural = 'User Summary Indices'
    
    def __str__(self):
        return f"{self.user.username} Summary (Index: {self.performance_index:.2f})"

class FitnessGoal(models.Model):
    """User fitness goals with progress tracking"""
    
    GOAL_STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fitness_goals')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    target_value = models.FloatField(help_text="Target value (calories, weight, etc.)")
    current_value = models.FloatField(default=0.0)
    unit = models.CharField(max_length=20, default='calories')
    target_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=GOAL_STATUS_CHOICES, default='active')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Fitness Goal'
        verbose_name_plural = 'Fitness Goals'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    @property
    def progress_percentage(self):
        """Calculate progress as percentage"""
        if self.target_value > 0:
            return min((self.current_value / self.target_value) * 100, 100)
        return 0

# ============ RANKING MODELS ============

class UserRanking(models.Model):
    """User rankings and leaderboard data"""
    
    RANKING_TYPE_CHOICES = [
        ('overall', 'Overall Performance'),
        ('calories', 'Total Calories Burned'),
        ('consistency', 'Workout Consistency'),
        ('improvement', 'Performance Improvement'),
        ('weekly', 'Weekly Performance'),
        ('monthly', 'Monthly Performance'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rankings')
    ranking_type = models.CharField(max_length=20, choices=RANKING_TYPE_CHOICES)
    
    # Ranking data
    rank = models.PositiveIntegerField()
    score = models.FloatField()
    percentile = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Percentile ranking (0-100)"
    )
    
    # Additional metrics
    total_participants = models.PositiveIntegerField()
    points_earned = models.FloatField(default=0.0)
    
    # Time period
    period_start = models.DateField()
    period_end = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Ranking'
        verbose_name_plural = 'User Rankings'
        unique_together = ['user', 'ranking_type', 'period_start', 'period_end']
        ordering = ['ranking_type', 'rank']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_ranking_type_display()} (Rank #{self.rank})"

class RankingHistory(models.Model):
    """Historical ranking data for trend analysis"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ranking_history')
    ranking_type = models.CharField(max_length=20, choices=UserRanking.RANKING_TYPE_CHOICES)
    
    previous_rank = models.PositiveIntegerField(null=True, blank=True)
    current_rank = models.PositiveIntegerField()
    rank_change = models.IntegerField(default=0)  # Positive = improvement
    
    previous_score = models.FloatField(null=True, blank=True)
    current_score = models.FloatField()
    score_change = models.FloatField(default=0.0)
    
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Ranking History'
        verbose_name_plural = 'Ranking Histories'
        unique_together = ['user', 'ranking_type', 'date']
        ordering = ['-date']
    
    def __str__(self):
        direction = "↑" if self.rank_change > 0 else "↓" if self.rank_change < 0 else "→"
        return f"{self.user.username} - {self.get_ranking_type_display()} {direction}"

class Achievement(models.Model):
    """User achievements and badges"""
    
    ACHIEVEMENT_TYPE_CHOICES = [
        ('milestone', 'Milestone'),
        ('streak', 'Streak'),
        ('performance', 'Performance'),
        ('consistency', 'Consistency'),
        ('improvement', 'Improvement'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=100)
    description = models.TextField()
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPE_CHOICES)
    points = models.PositiveIntegerField(default=0)
    
    # Achievement metadata
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class or emoji")
    rarity = models.CharField(
        max_length=10,
        choices=[('common', 'Common'), ('rare', 'Rare'), ('epic', 'Epic'), ('legendary', 'Legendary')],
        default='common'
    )
    
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Achievement'
        verbose_name_plural = 'Achievements'
        unique_together = ['user', 'title']
        ordering = ['-earned_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
