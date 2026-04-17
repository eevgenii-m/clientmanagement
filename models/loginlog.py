"""
LoginLog model — records every login attempt (success and failure).
Signal handlers are wired up in models/apps.py via ready().
"""
from django.db import models
from django.contrib.auth.models import User


def get_client_ip(request):
    """Return the real client IP, honouring X-Forwarded-For."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


class LoginLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='login_logs',
    )
    username_attempted = models.CharField(max_length=150, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    success = models.BooleanField(default=False, db_index=True)
    user_agent = models.CharField(max_length=300, blank=True, default='')

    class Meta:
        app_label = 'models'
        ordering = ['-timestamp']

    def __str__(self):
        status = 'OK' if self.success else 'FAIL'
        return f"{self.username_attempted} [{status}] {self.timestamp}"


# ── Signal handler functions ─────────────────────────────────────────────────
# These are connected to Django auth signals in models/apps.py ready().

def log_successful_login(sender, request, user, **kwargs):
    """Called by user_logged_in signal."""
    try:
        LoginLog.objects.create(
            user=user,
            username_attempted=user.username,
            ip_address=get_client_ip(request),
            success=True,
            user_agent=(request.META.get('HTTP_USER_AGENT', '') or '')[:300],
        )
    except Exception:
        pass  # Never crash on logging


def log_failed_login(sender, credentials, request, **kwargs):
    """Called by user_login_failed signal."""
    try:
        LoginLog.objects.create(
            username_attempted=(credentials.get('username') or '')[:150],
            ip_address=get_client_ip(request),
            success=False,
            user_agent=(request.META.get('HTTP_USER_AGENT', '') or '')[:300],
        )
    except Exception:
        pass  # Never crash on logging
