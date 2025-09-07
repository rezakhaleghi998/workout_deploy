from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.db.models import Count, Avg, Sum
from django.http import HttpResponse
from django.utils import timezone
import csv
from datetime import datetime, timedelta
from .models import (
    User, UserProfile, WorkoutSession, PerformanceMetric, PerformanceMetrics, UserRanking, Achievement,
    WorkoutAnalysis, FitnessPerformanceIndex, WellnessPlan
)

# ============ RAILWAY-OPTIMIZED USER ADMIN ============

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """Railway-optimized admin interface for User model"""
    
    list_display = [
        'username', 'email', 'get_full_name', 'fitness_level', 
        'total_workouts', 'total_calories_burned', 'get_fitness_score',
        'get_bmi_status', 'is_active', 'date_joined'
    ]
    list_filter = [
        'fitness_level', 'is_active', 'is_staff', 'date_joined', 
        'total_workouts'
    ]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    list_per_page = 25
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Fitness Profile', {
            'fields': (
                'height', 'weight', 'age', 'fitness_level',
                'total_workouts', 'total_calories_burned'
            ),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = BaseUserAdmin.readonly_fields + [
        'total_workouts', 'total_calories_burned', 'created_at', 'updated_at'
    ]
    
    actions = ['export_users_csv', 'update_user_stats']
    
    def get_fitness_score(self, obj):
        """Display fitness score with color coding"""
        score = obj.fitness_score
        if score >= 80:
            color = 'green'
        elif score >= 60:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, score
        )
    get_fitness_score.short_description = 'Fitness Score'
    get_fitness_score.admin_order_field = 'total_workouts'
    
    def get_bmi_status(self, obj):
        """Display BMI with status"""
        bmi = obj.bmi
        if bmi is None:
            return 'N/A'
        
        if 18.5 <= bmi <= 24.9:
            status = 'Normal'
            color = 'green'
        elif 25 <= bmi <= 29.9:
            status = 'Overweight'
            color = 'orange'
        else:
            status = 'Obese' if bmi >= 30 else 'Underweight'
            color = 'red'
            
        return format_html(
            '<span style="color: {};">{:.1f} ({})</span>',
            color, bmi, status
        )
    get_bmi_status.short_description = 'BMI Status'
    
    def export_users_csv(self, request, queryset):
        """Export selected users to CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Username', 'Email', 'Full Name', 'Fitness Level', 
            'Height', 'Weight', 'BMI', 'Total Workouts', 
            'Total Calories', 'Fitness Score', 'Date Joined'
        ])
        
        for user in queryset:
            writer.writerow([
                user.username,
                user.email,
                user.get_full_name(),
                user.fitness_level,
                user.height or '',
                user.weight or '',
                user.bmi or '',
                user.total_workouts,
                user.total_calories_burned,
                user.fitness_score,
                user.date_joined.strftime('%Y-%m-%d')
            ])
            
        return response
    export_users_csv.short_description = "Export selected users to CSV"
    
    def update_user_stats(self, request, queryset):
        """Update workout statistics for selected users"""
        for user in queryset:
            user.update_workout_stats()
        
        self.message_user(
            request,
            f"Updated statistics for {queryset.count()} users."
        )
    update_user_stats.short_description = "Update workout statistics"

# ============ RAILWAY WORKOUT SESSION ADMIN ============

@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    """Railway-optimized admin interface for WorkoutSession model"""
    
    list_display = [
        'get_user_link', 'workout_type', 'duration_minutes', 
        'calories_burned', 'intensity', 'performance_rating',
        'get_efficiency_score', 'date'
    ]
    list_filter = [
        'workout_type', 'intensity', 'performance_rating', 
        'date', 'user__fitness_level'
    ]
    search_fields = [
        'user__username', 'user__email', 'workout_type', 'notes'
    ]
    ordering = ['-date']
    date_hierarchy = 'date'
    list_per_page = 30
    
    autocomplete_fields = ['user']
    
    fieldsets = (
        ('Workout Details', {
            'fields': (
                'user', 'workout_type', 'duration_minutes', 
                'calories_burned', 'intensity'
            )
        }),
        ('Performance Metrics', {
            'fields': (
                'heart_rate_avg', 'performance_rating'
            )
        }),
        ('Additional Info', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['export_workouts_csv', 'calculate_weekly_summary']
    
    def get_user_link(self, obj):
        """Display user as clickable link"""
        return format_html(
            '<a href="/admin/fitness_app/user/{}/change/">{}</a>',
            obj.user.id, obj.user.username
        )
    get_user_link.short_description = 'User'
    get_user_link.admin_order_field = 'user__username'
    
    def get_efficiency_score(self, obj):
        """Calculate and display workout efficiency"""
        if obj.duration_minutes > 0:
            efficiency = obj.calories_burned / obj.duration_minutes
            if efficiency >= 10:
                color = 'green'
            elif efficiency >= 7:
                color = 'orange'
            else:
                color = 'red'
                
            return format_html(
                '<span style="color: {};">{:.1f} cal/min</span>',
                color, efficiency
            )
        return 'N/A'
    get_efficiency_score.short_description = 'Efficiency'
    
    def export_workouts_csv(self, request, queryset):
        """Export selected workouts to CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="workouts_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'User', 'Date', 'Workout Type', 'Duration (min)', 
            'Calories Burned', 'Intensity', 'Heart Rate', 
            'Performance Rating', 'Efficiency (cal/min)', 'Notes'
        ])
        
        for workout in queryset:
            efficiency = workout.calories_burned / workout.duration_minutes if workout.duration_minutes > 0 else 0
            writer.writerow([
                workout.user.username,
                workout.date.strftime('%Y-%m-%d %H:%M'),
                workout.workout_type,
                workout.duration_minutes,
                workout.calories_burned,
                workout.intensity,
                workout.heart_rate_avg or '',
                workout.performance_rating,
                f"{efficiency:.1f}",
                workout.notes
            ])
            
        return response
    export_workouts_csv.short_description = "Export selected workouts to CSV"

# ============ RAILWAY PERFORMANCE METRICS ADMIN ============

@admin.register(PerformanceMetric)
class PerformanceMetricAdmin(admin.ModelAdmin):
    """Railway-optimized admin interface for PerformanceMetric model"""
    
    list_display = [
        'get_user_link', 'date', 'weight', 'get_bmi_display',
        'body_fat_percentage', 'performance_index', 'get_health_status'
    ]
    list_filter = ['date', 'user__fitness_level']
    search_fields = ['user__username', 'user__email']
    ordering = ['-date']
    date_hierarchy = 'date'
    list_per_page = 25
    
    autocomplete_fields = ['user']
    
    fieldsets = (
        ('Basic Metrics', {
            'fields': ('user', 'date', 'weight')
        }),
        ('Body Composition', {
            'fields': ('body_fat_percentage', 'muscle_mass')
        }),
        ('Health Metrics', {
            'fields': (
                'resting_heart_rate', 'blood_pressure_systolic', 
                'blood_pressure_diastolic'
            )
        }),
        ('Performance', {
            'fields': ('performance_index',)
        }),
    )
    
    actions = ['export_metrics_csv', 'calculate_performance_index']
    
    def get_user_link(self, obj):
        """Display user as clickable link"""
        return format_html(
            '<a href="/admin/fitness_app/user/{}/change/">{}</a>',
            obj.user.id, obj.user.username
        )
    get_user_link.short_description = 'User'
    get_user_link.admin_order_field = 'user__username'
    
    def get_bmi_display(self, obj):
        """Display BMI with color coding"""
        bmi = obj.bmi
        if bmi is None:
            return 'N/A'
            
        if 18.5 <= bmi <= 24.9:
            color = 'green'
            status = 'Normal'
        elif 25 <= bmi <= 29.9:
            color = 'orange'
            status = 'Overweight'
        else:
            color = 'red'
            status = 'Obese' if bmi >= 30 else 'Underweight'
            
        return format_html(
            '<span style="color: {};">{:.1f} ({})</span>',
            color, bmi, status
        )
    get_bmi_display.short_description = 'BMI'
    
    def get_health_status(self, obj):
        """Display overall health status"""
        score = obj.performance_index
        if score >= 80:
            status = 'Excellent'
            color = 'green'
        elif score >= 60:
            status = 'Good'
            color = 'blue'
        elif score >= 40:
            status = 'Fair'
            color = 'orange'
        else:
            status = 'Poor'
            color = 'red'
            
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, status
        )
    get_health_status.short_description = 'Health Status'
    
    def calculate_performance_index(self, request, queryset):
        """Recalculate performance index for selected metrics"""
        updated = 0
        for metric in queryset:
            metric.calculate_performance_index()
            metric.save()
            updated += 1
            
        self.message_user(
            request,
            f"Updated performance index for {updated} records."
        )
    calculate_performance_index.short_description = "Recalculate performance index"

# ============ EXISTING ADMIN REGISTRATIONS ============

# Keep existing admin registrations for other models

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
