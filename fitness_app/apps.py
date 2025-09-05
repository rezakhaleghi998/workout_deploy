from django.apps import AppConfig


class FitnessAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fitness_app'
    verbose_name = 'Fitness Tracker'
    
    def ready(self):
        """Import signal handlers when app is ready"""
        try:
            import fitness_app.signals
        except ImportError:
            pass
