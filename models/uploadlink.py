from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import datetime, timedelta
import uuid, os

def calc_expiry_upload():
    return datetime.today().date() + timedelta(days=7)

def upload_to_client(instance, filename):
    return os.path.join('client_uploads', instance.upload_link.unid.hex, filename)

class UploadLink(models.Model):
    unid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField('Title / Purpose', max_length=120)
    description = models.TextField('Instructions for client', blank=True, default='')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    expires_on = models.DateField(default=calc_expiry_upload)
    is_active = models.BooleanField(default=True)
    max_files = models.IntegerField(default=10)

    def is_expired(self):
        return self.expires_on < datetime.today().date()

    def is_available(self):
        return self.is_active and not self.is_expired()

    def get_upload_url(self):
        return reverse('client_upload_page', kwargs={'linkuuid': self.unid})

    def __str__(self):
        return self.title

class ClientUploadedFile(models.Model):
    upload_link = models.ForeignKey(UploadLink, on_delete=models.CASCADE, related_name='uploaded_files')
    uplfile = models.FileField(upload_to=upload_to_client, max_length=255)
    original_filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    file_size = models.BigIntegerField(default=0)

    @property
    def file_size_display(self):
        size = self.file_size or 0
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.1f} GB"

    def __str__(self):
        return self.original_filename