from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.http import HttpResponse
import csv
from .models import User, WorkoutSession, WorkoutAnalysis, FitnessPerformanceIndex, WellnessPlan

# ============ USER ADMIN ============

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'fitness_level', 'height', 'weight', 'created_at')
    list_filter = ('fitness_level', 'created_at', 'is_staff')
    search_fields = ('username', 'email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Fitness Profile', {
            'fields': ('height', 'weight', 'age', 'fitness_level', 'created_at', 'updated_at')
        }),
    )

# ============ WORKOUT ADMIN ============

@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'workout_type', 'duration_minutes', 'calories_burned', 'intensity', 'date')
    list_filter = ('workout_type', 'intensity', 'date')
    search_fields = ('user__username', 'workout_type')
    date_hierarchy = 'date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(WorkoutAnalysis)
class WorkoutAnalysisAdmin(admin.ModelAdmin):
    list_display = ('user', 'workout_type', 'duration_minutes', 'calories_burned', 'performance_score', 'session_date')
    list_filter = ('workout_type', 'intensity_level', 'session_date')
    search_fields = ('user__username', 'workout_type')
    date_hierarchy = 'session_date'
    readonly_fields = ('session_date',)
    
    actions = ['export_as_csv']
    
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}.csv'
        writer = csv.writer(response)
        
        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
        
        return response
    
    export_as_csv.short_description = "Export Selected as CSV"

@admin.register(FitnessPerformanceIndex)
class FitnessPerformanceIndexAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'performance_index', 'strength_score', 'endurance_score')
    list_filter = ('date',)
    search_fields = ('user__username',)
    date_hierarchy = 'date'

@admin.register(WellnessPlan)
class WellnessPlanAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan_name', 'plan_type', 'duration_weeks', 'is_active', 'created_at')
    list_filter = ('plan_type', 'is_active', 'created_at')
    search_fields = ('user__username', 'plan_name')
    date_hierarchy = 'created_at'
