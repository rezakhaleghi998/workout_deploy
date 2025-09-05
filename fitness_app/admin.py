from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum, Avg
from .models import (
    User, UserProfile, WorkoutSession, ExerciseType, WorkoutGoal,
    PerformanceMetrics, UserSummaryIndex, FitnessGoal,
    UserRanking, RankingHistory, Achievement
)

# ============ USER ADMIN ============

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ['age', 'weight', 'height', 'gender', 'fitness_level', 'bmi', 'bmr']
    readonly_fields = ['bmi', 'bmr']

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    list_display = ['username', 'email', 'full_name', 'total_workouts', 'is_active', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Fitness Tracking', {'fields': ('total_workouts',)}),
    )
    
    def full_name(self, obj):
        return obj.get_full_name()
    full_name.short_description = 'Full Name'

# ============ WORKOUT ADMIN ============

@admin.register(ExerciseType)
class ExerciseTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'calories_per_hour', 'workout_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    def workout_count(self, obj):
        return obj.workout_sessions.count()
    workout_count.short_description = 'Total Workouts'

@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'exercise_type', 'duration_minutes', 'calories_burned', 'intensity', 'date']
    list_filter = ['exercise_type', 'intensity', 'date', 'created_at']
    search_fields = ['user__username', 'exercise_type__name', 'notes']
    ordering = ['-date']
    date_hierarchy = 'date'
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Workout Details', {
            'fields': ('user', 'exercise_type', 'duration_minutes', 'calories_burned', 'intensity')
        }),
        ('Additional Info', {
            'fields': ('notes', 'date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(WorkoutGoal)
class WorkoutGoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'goal_type', 'target_calories_per_week', 'target_workouts_per_week', 'is_active']
    list_filter = ['goal_type', 'is_active', 'created_at']
    search_fields = ['user__username', 'description']
    ordering = ['-created_at']

# ============ PERFORMANCE ADMIN ============

@admin.register(PerformanceMetrics)
class PerformanceMetricsAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'date', 'overall_fitness_index', 'fitness_grade_display',
        'total_calories_burned', 'calorie_efficiency'
    ]
    list_filter = ['date', 'created_at']
    search_fields = ['user__username']
    ordering = ['-date']
    date_hierarchy = 'date'
    
    readonly_fields = ['overall_fitness_index', 'created_at', 'updated_at']
    
    fieldsets = (
        ('User & Date', {
            'fields': ('user', 'date')
        }),
        ('Fitness Scores', {
            'fields': ('cardiovascular_score', 'strength_score', 'flexibility_score', 'endurance_score', 'overall_fitness_index')
        }),
        ('Performance Data', {
            'fields': ('total_calories_burned', 'total_workout_time', 'workout_frequency', 'calorie_efficiency', 'consistency_score')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def fitness_grade_display(self, obj):
        grade = obj.get_fitness_grade()
        if grade in ['A+', 'A', 'A-']:
            color = 'green'
        elif grade in ['B+', 'B', 'B-']:
            color = 'blue'
        elif grade in ['C+', 'C', 'C-']:
            color = 'orange'
        else:
            color = 'red'
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, grade)
    fitness_grade_display.short_description = 'Fitness Grade'

@admin.register(UserSummaryIndex)
class UserSummaryIndexAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'performance_index', 'total_sessions', 'total_calories',
        'global_rank', 'percentile', 'last_calculated'
    ]
    list_filter = ['last_calculated']
    search_fields = ['user__username']
    ordering = ['-performance_index']
    readonly_fields = ['last_calculated']

@admin.register(FitnessGoal)
class FitnessGoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'progress_display', 'status', 'target_date']
    list_filter = ['status', 'target_date', 'created_at']
    search_fields = ['user__username', 'title', 'description']
    ordering = ['-created_at']
    
    def progress_display(self, obj):
        progress = obj.progress_percentage
        if progress >= 100:
            color = 'green'
        elif progress >= 75:
            color = 'blue'
        elif progress >= 50:
            color = 'orange'
        else:
            color = 'red'
        return format_html('<span style="color: {}; font-weight: bold;">{:.1f}%</span>', color, progress)
    progress_display.short_description = 'Progress'

# ============ RANKING ADMIN ============

@admin.register(UserRanking)
class UserRankingAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'ranking_type', 'rank', 'score', 'percentile',
        'period_start', 'period_end'
    ]
    list_filter = ['ranking_type', 'period_start', 'period_end']
    search_fields = ['user__username']
    ordering = ['ranking_type', 'rank']

@admin.register(RankingHistory)
class RankingHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'ranking_type', 'current_rank', 'rank_change_display',
        'current_score', 'date'
    ]
    list_filter = ['ranking_type', 'date']
    search_fields = ['user__username']
    ordering = ['-date']
    
    def rank_change_display(self, obj):
        change = obj.rank_change
        if change > 0:
            return format_html('<span style="color: green;">↑ {}</span>', change)
        elif change < 0:
            return format_html('<span style="color: red;">↓ {}</span>', abs(change))
        else:
            return format_html('<span style="color: gray;">→ 0</span>')
    rank_change_display.short_description = 'Rank Change'

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'achievement_type', 'rarity', 'points', 'earned_at']
    list_filter = ['achievement_type', 'rarity', 'earned_at']
    search_fields = ['user__username', 'title', 'description']
    ordering = ['-earned_at']

# ============ CUSTOM ADMIN ACTIONS ============

@admin.action(description='Recalculate performance metrics')
def recalculate_performance_metrics(modeladmin, request, queryset):
    """Recalculate performance metrics for selected users"""
    from .views import update_user_performance_metrics
    
    count = 0
    for user in queryset:
        # Get latest workout session
        latest_workout = WorkoutSession.objects.filter(user=user).order_by('-date').first()
        if latest_workout:
            update_user_performance_metrics(user, latest_workout)
            count += 1
    
    modeladmin.message_user(
        request,
        f'Performance metrics recalculated for {count} users.'
    )

@admin.action(description='Update summary indices')
def update_summary_indices(modeladmin, request, queryset):
    """Update summary indices for selected users"""
    from .views import update_user_summary_index
    
    count = 0
    for user in queryset:
        summary, created = UserSummaryIndex.objects.get_or_create(user=user)
        update_user_summary_index(user, summary)
        count += 1
    
    modeladmin.message_user(
        request,
        f'Summary indices updated for {count} users.'
    )

# Add actions to UserAdmin
UserAdmin.actions = [recalculate_performance_metrics, update_summary_indices]

# ============ ADMIN SITE CUSTOMIZATION ============

admin.site.site_header = 'Fitness Tracker Administration'
admin.site.site_title = 'Fitness Tracker Admin'
admin.site.index_title = 'Welcome to Fitness Tracker Administration'

# Custom admin dashboard stats
class AdminDashboardMixin:
    """Mixin to add dashboard stats to admin"""
    
    def changelist_view(self, request, extra_context=None):
        # Get some basic stats
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        total_workouts = WorkoutSession.objects.count()
        total_calories = WorkoutSession.objects.aggregate(
            total=Sum('calories_burned')
        )['total'] or 0
        
        extra_context = extra_context or {}
        extra_context.update({
            'total_users': total_users,
            'active_users': active_users,
            'total_workouts': total_workouts,
            'total_calories': total_calories,
        })
        
        return super().changelist_view(request, extra_context=extra_context)
