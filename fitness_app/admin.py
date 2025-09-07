from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.db.models import Count, Avg
from .models import (
    User, UserProfile, WorkoutSession, PerformanceMetrics, UserRanking, Achievement,
    WorkoutAnalysis, FitnessPerformanceIndex, WellnessPlan
)

# ============ USER ADMIN ============

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model"""
    list_display = ['username', 'email', 'first_name', 'last_name', 'total_workouts', 'get_total_analyses', 'is_active', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Fitness Info', {'fields': ('total_workouts',)}),
    )
    readonly_fields = ['total_workouts']
    
    def get_total_analyses(self, obj):
        return obj.workout_analyses.count()
    get_total_analyses.short_description = 'Total Analyses'
    get_total_analyses.admin_order_field = 'workout_analyses__count'

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

admin.site.site_header = "Workout Calorie Predictor v2.1 Admin Panel"
admin.site.site_title = "Workout Predictor Admin"
admin.site.index_title = "Welcome to Workout Calorie Predictor Administration"

# ============ WORKOUT ANALYSIS ADMIN ============

@admin.register(WorkoutAnalysis)
class WorkoutAnalysisAdmin(admin.ModelAdmin):
    """Comprehensive admin interface for 14-page workout analysis data"""
    list_display = ('user', 'workout_type', 'analysis_type', 'predicted_calories', 'duration_minutes', 'efficiency_grade', 'fitness_performance_index', 'created_at')
    list_filter = ('workout_type', 'analysis_type', 'gender', 'activity_level', 'efficiency_grade', 'intensity_level', 'created_at')
    search_fields = ('user__username', 'workout_type', 'burn_efficiency')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('User & Analysis Type', {
            'fields': ('user', 'analysis_type')
        }),
        ('Personal Data', {
            'fields': ('age', 'gender', 'height_cm', 'weight_kg')
        }),
        ('Workout Details', {
            'fields': ('workout_type', 'duration_minutes', 'heart_rate_bpm', 'distance_km', 'activity_level', 'sleep_hours', 'mood_before')
        }),
        ('Calorie Results', {
            'fields': ('predicted_calories', 'calories_per_minute', 'calorie_range_min', 'calorie_range_max', 'efficiency_grade', 'burn_efficiency')
        }),
        ('Performance Index', {
            'fields': ('fitness_performance_index', 'consistency_score', 'performance_score', 'variety_score', 'intensity_score'),
            'classes': ('collapse',)
        }),
        ('Rankings & Statistics', {
            'fields': ('user_ranking_overall', 'user_ranking_fitness', 'user_ranking_consistency', 'percentile_rank', 'total_users_in_comparison'),
            'classes': ('collapse',)
        }),
        ('Pace & Distance', {
            'fields': ('average_pace_min_per_km', 'speed_kmh', 'calories_per_km'),
            'classes': ('collapse',)
        }),
        ('Mood Analysis', {
            'fields': ('predicted_mood_after', 'mood_improvement_levels'),
            'classes': ('collapse',)
        }),
        ('AI Recommendations', {
            'fields': ('ai_diet_recommendations', 'ai_workout_recommendations', 'ai_sleep_recommendations'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['export_to_csv', 'generate_performance_report']
    
    def export_to_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="workout_analyses.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Username', 'Analysis Type', 'Workout Type', 'Duration (min)', 'Predicted Calories', 
            'Efficiency Grade', 'Performance Index', 'Overall Ranking', 'Percentile', 'Date'
        ])
        
        for analysis in queryset:
            writer.writerow([
                analysis.user.username,
                analysis.analysis_type,
                analysis.workout_type,
                analysis.duration_minutes,
                analysis.predicted_calories,
                analysis.efficiency_grade or 'N/A',
                analysis.fitness_performance_index or 'N/A',
                analysis.user_ranking_overall or 'N/A',
                analysis.percentile_rank or 'N/A',
                analysis.created_at.strftime('%Y-%m-%d %H:%M')
            ])
        
        return response
    export_to_csv.short_description = "Export selected analyses to CSV"
    
    def generate_performance_report(self, request, queryset):
        from django.http import HttpResponse
        import json
        
        data = []
        for analysis in queryset:
            data.append({
                'user': analysis.user.username,
                'workout_type': analysis.workout_type,
                'calories': float(analysis.predicted_calories),
                'performance_index': float(analysis.fitness_performance_index) if analysis.fitness_performance_index else None,
                'consistency_score': float(analysis.consistency_score) if analysis.consistency_score else None,
                'date': analysis.created_at.isoformat()
            })
        
        response = HttpResponse(json.dumps(data, indent=2), content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="performance_report.json"'
        return response
    generate_performance_report.short_description = "Generate performance report (JSON)"

@admin.register(FitnessPerformanceIndex)
class FitnessPerformanceIndexAdmin(admin.ModelAdmin):
    """Admin interface for detailed Fitness Performance Index tracking"""
    list_display = ('user', 'overall_score', 'fitness_level', 'progress_status', 'consistency_percentage', 'performance_percentage', 'created_at')
    list_filter = ('fitness_level', 'progress_status', 'created_at')
    search_fields = ('user__username', 'fitness_level', 'progress_status')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('User & Analysis', {
            'fields': ('user', 'workout_analysis')
        }),
        ('Overall Performance', {
            'fields': ('overall_score', 'fitness_level', 'progress_status')
        }),
        ('Component Scores', {
            'fields': (
                ('consistency_score', 'consistency_percentage'),
                ('performance_score', 'performance_percentage'),
                ('variety_score', 'variety_percentage'),
                ('intensity_score', 'intensity_percentage')
            )
        }),
        ('Progress Tracking', {
            'fields': (
                ('weekly_change', 'weekly_change_percentage'),
                ('monthly_change', 'monthly_change_percentage')
            ),
            'classes': ('collapse',)
        }),
        ('Insights', {
            'fields': ('insights',),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(WellnessPlan)
class WellnessPlanAdmin(admin.ModelAdmin):
    """Admin interface for AI-generated wellness plans"""
    list_display = ('user', 'total_daily_calories_needed', 'basal_metabolic_rate', 'recommended_intake', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('User & Analysis', {
            'fields': ('user', 'workout_analysis')
        }),
        ('Caloric Requirements', {
            'fields': ('total_daily_calories_needed', 'basal_metabolic_rate', 'activity_calories', 'workout_calories', 'recommended_intake')
        }),
        ('AI Recommendations', {
            'fields': (
                'personalized_diet_plan',
                'advanced_workout_programming', 
                'sleep_recovery_optimization',
                'supplement_recommendations',
                'progress_tracking_guidelines',
                'lifestyle_integration'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
