from django.apps import AppConfig

class StepsTrackingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'steps_tracking'

    def ready(self):
        import steps_tracking.signals