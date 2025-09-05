from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserProfile, WorkoutSession, PerformanceMetrics, UserRanking, Achievement

# ============ USER ADMIN ============

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model"""
    list_display = ['username', 'email', 'first_name', 'last_name', 'total_workouts', 'is_active', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Fitness Info', {'fields': ('total_workouts',)}),
    )
    readonly_fields = ['total_workouts']

# ============ PROFILE ADMIN ============

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile model"""
    list_display = ['user', 'fitness_level', 'height', 'weight']
    list_filter = ['fitness_level', 'created_at']
    search_fields = ['user__username', 'user__email']
    ordering = ['-created_at']

# ============ WORKOUT ADMIN ============

@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    """Admin interface for WorkoutSession model"""
    list_display = ['user', 'workout_type', 'date', 'duration', 'intensity', 'calories_burned']
    list_filter = ['workout_type', 'intensity', 'date']
    search_fields = ['user__username', 'workout_type', 'notes']
    ordering = ['-date']
    date_hierarchy = 'date'

# ============ PERFORMANCE ADMIN ============

@admin.register(PerformanceMetrics)
class PerformanceMetricsAdmin(admin.ModelAdmin):
    """Admin interface for PerformanceMetrics model"""
    list_display = ['user', 'date', 'weight', 'cardiovascular_fitness', 'strength_level']
    list_filter = ['date', 'cardiovascular_fitness', 'strength_level']
    search_fields = ['user__username']
    ordering = ['-date']
    date_hierarchy = 'date'

# ============ RANKING ADMIN ============

@admin.register(UserRanking)
class UserRankingAdmin(admin.ModelAdmin):
    """Admin interface for UserRanking model"""
    list_display = ['user', 'level', 'total_points', 'rank']
    list_filter = ['level', 'rank']
    search_fields = ['user__username']
    ordering = ['rank']

# ============ ACHIEVEMENT ADMIN ============

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    """Admin interface for Achievement model"""
    list_display = ['user', 'title', 'achievement_type', 'points_awarded', 'achieved_at']
    list_filter = ['achievement_type', 'achieved_at']
    search_fields = ['user__username', 'title', 'description']
    ordering = ['-achieved_at']
    date_hierarchy = 'achieved_at'

# ============ ADMIN CUSTOMIZATION ============

admin.site.site_header = "Fitness Tracker Admin"
admin.site.site_title = "Fitness Tracker"
admin.site.index_title = "Welcome to Fitness Tracker Administration"
