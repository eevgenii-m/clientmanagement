"""
Custom authentication backend that accepts email address OR username.
Email lookup is case-insensitive; falls back gracefully to standard username auth.
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class EmailOrUsernameBackend(ModelBackend):
    """
    Allow login with either:
      - username  (existing behaviour, unchanged)
      - email     (case-insensitive lookup)
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = None

        # 1. Try exact username match first (keeps existing logins working)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            pass

        # 2. Fall back to case-insensitive email lookup
        if user is None and username and '@' in username:
            try:
                user = User.objects.get(email__iexact=username)
            except User.DoesNotExist:
                pass
            except User.MultipleObjectsReturned:
                # Multiple accounts share the email — cannot resolve safely
                return None

        if user is None:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None
