from django.urls import path
from . import views

app_name = 'fitness_app'

urlpatterns = [
    # API root
    path('', views.api_root, name='api_root'),
    
    # Authentication endpoints
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', views.user_profile, name='profile'),

    # Workout endpoints
    path('workouts/', views.workout_sessions, name='workout_sessions'),
    path('analytics/', views.workout_analytics, name='workout_analytics'),

    # Performance endpoints
    path('performance/', views.performance_metrics, name='performance_metrics'),

    # Ranking endpoints
    path('rankings/', views.user_rankings, name='user_rankings'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('achievements/', views.user_achievements, name='achievements'),
]
