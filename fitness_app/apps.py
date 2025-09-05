from django.apps import AppConfig


class FitnessAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fitness_app'
    verbose_name = 'Fitness Tracker'
    
    def ready(self):
        """App is ready - signals removed for deployment safety"""
        pass
