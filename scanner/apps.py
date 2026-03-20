from django.apps import AppConfig

class ScannerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scanner'
    verbose_name = 'Content Scanner' # Optional: Makes the app name look cleaner in the Admin UI