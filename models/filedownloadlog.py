from django.db import models
from models.sharedfile import SharedFile


class FileDownloadLog(models.Model):
    shared_file = models.ForeignKey(SharedFile, on_delete=models.CASCADE,
                                    related_name='download_logs')
    downloaded_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    referer = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return '{} — {} — {}'.format(
            self.shared_file.original_filename,
            self.ip_address,
            self.downloaded_at,
        )
