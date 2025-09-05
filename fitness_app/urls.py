from django.urls import path, include
from . import views

app_name = 'fitness_app'

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.register_user, name='register'),
    path('auth/login/', views.login_user, name='login'),
    path('auth/logout/', views.logout_user, name='logout'),
    path('auth/profile/', views.user_profile, name='profile'),
    
    # Workout endpoints
    path('workouts/sessions/', views.workout_sessions, name='workout_sessions'),
    path('workouts/exercises/', views.exercise_types, name='exercise_types'),
    path('workouts/goals/', views.workout_goals, name='workout_goals'),
    
    # Performance endpoints
    path('performance/metrics/', views.performance_metrics, name='performance_metrics'),
    path('performance/summary/', views.user_summary_index, name='summary_index'),
    path('performance/goals/', views.fitness_goals, name='fitness_goals'),
    path('performance/analytics/', views.workout_analytics, name='workout_analytics'),
    
    # Ranking endpoints
    path('rankings/user/', views.user_rankings, name='user_rankings'),
    path('rankings/leaderboard/', views.leaderboard, name='leaderboard'),
    path('rankings/achievements/', views.user_achievements, name='achievements'),
]
