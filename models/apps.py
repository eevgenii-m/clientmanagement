from django.apps import AppConfig


class ModelsConfig(AppConfig):
    name = 'models'

    def ready(self):
        """Connect auth signals to login logging handlers."""
        try:
            from django.contrib.auth.signals import user_logged_in, user_login_failed
            from models.loginlog import log_successful_login, log_failed_login
            user_logged_in.connect(log_successful_login)
            user_login_failed.connect(log_failed_login)
        except Exception:
            pass  # Gracefully skip if DB not yet migrated
