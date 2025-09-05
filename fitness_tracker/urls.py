"""
URL configuration for fitness_tracker project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include('fitness_app.urls')),
    
    # Main page
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    
    # Login page
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
