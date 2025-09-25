# user_profile/apps.py
from django.apps import AppConfig

class UserProfileConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_profile'
    
    def ready(self):
        # Sinyalleri kaydet
        import user_profile.signals