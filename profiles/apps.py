from django.apps import AppConfig

class ProfilesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "profiles"

    def ready(self):
        # Import signals so a profile is auto-created when a new User is created
        import profiles.signals  # noqa
