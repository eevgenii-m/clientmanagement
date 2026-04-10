from django.db import models
from datetime import datetime, timedelta, timezone
from clientmanagement import sendemail
from django.conf import settings
from clientmanagement.widget import quill
import pytz


def time_now(instance=None):
    return datetime.now(pytz.utc)


class SystemUpdates(models.Model):
    
    version = models.CharField('Version', max_length=50, null=False, blank=False)
    postedon = models.DateTimeField('Update time', default=time_now, null=False, blank=False)
    createdon = models.DateTimeField('Created time', default=time_now, null=False, blank=False)
    author = models.CharField('Update author', max_length=120, null=True, blank=True)
    tittle = models.CharField('Tittle', default='', max_length=160, null=False, blank=False)
    wassent = models.BooleanField('Was sent', null=False, blank=False, default=False)
    newstext = models.TextField('News in text format')
    
    def __str__(self):
        return 'Updates for ' + self.version

    def editable(self):
        if datetime.now(pytz.utc) - self.createdon > timedelta(minutes=settings.TIME_TO_EDIT):
            return False
        else:
            return True

    def sendemail(self):
        if (not self.wassent):
            self.wassent = True
            self.save()
            sendemail.sendemaileveryone('emails/newpostemail.htm', {'post':self}, "New post: " + self.tittle)
    
    def get_quill_object(self):
        return quill.QuillObject(self.newstext)


def getCurrentVersion():
    try:
        latest_update = SystemUpdates.objects.all().order_by('-postedon')[0]
    except Exception:
        return "1.0.0"
    return latest_update.version
