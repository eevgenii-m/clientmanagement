from django.db import models
from datetime import datetime, date
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.models import User
import uuid, os, pytz


def shared_file_upload_to(instance, filename):
    return os.path.join('shared', filename)


class SharedFile(models.Model):
    unid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='shared_files')
    uplfile = models.FileField(upload_to=shared_file_upload_to, max_length=500,
                               null=False, blank=False, verbose_name='File')
    original_filename = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField('Description', max_length=300, null=True, blank=True)
    createdon = models.DateTimeField('Uploaded on', auto_now_add=True, null=False, blank=False)
    expireon = models.DateField('Expires on', null=True, blank=True)
    downloads = models.IntegerField('Downloads used', default=0, null=False, blank=False)
    max_downloads = models.IntegerField('Maximum downloads', null=True, blank=True)

    def __str__(self):
        return self.original_filename or str(self.unid)

    def get_download_url(self):
        return reverse('download_shared_file', kwargs={'fileuuid': self.unid})

    def get_full_download_url(self):
        return settings.EMAIL_HOST_LINK + self.get_download_url()

    def filename_display(self):
        if self.original_filename:
            return self.original_filename
        if self.uplfile:
            return os.path.basename(self.uplfile.name)
        return '(no file)'

    def file_size_display(self):
        try:
            size = self.uplfile.size
            if size < 1024:
                return '{} B'.format(size)
            elif size < 1024 * 1024:
                return '{} KB'.format(size // 1024)
            else:
                return '{:.1f} MB'.format(size / (1024 * 1024))
        except Exception:
            return '—'

    def is_expired(self):
        if self.expireon is None:
            return False
        return self.expireon < date.today()

    def is_download_limit_reached(self):
        if self.max_downloads is None:
            return False
        return self.downloads >= self.max_downloads

    def is_available(self):
        return not self.is_expired() and not self.is_download_limit_reached()

    def days_left(self):
        if self.expireon is None:
            return None
        delta = self.expireon - date.today()
        return delta.days

    def createtime(self):
        return self.createdon.astimezone(pytz.timezone('America/New_York'))
