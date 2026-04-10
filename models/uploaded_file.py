from django.db import models
from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.urls import reverse
import pytz, uuid, os, random
from models import ticket, ticket_comment
from django.core.files.storage import default_storage
from django.utils.encoding import smart_str
from urllib.parse import quote, unquote
from django.http import HttpResponse, FileResponse
from clientmanagement import error_views


class UploadedFileTicket(models.Model):
    for_ticket = models.ForeignKey(ticket.Ticket, on_delete=models.CASCADE, null=False, related_name="files")
    createdon = models.DateTimeField("Created time", auto_now_add=True, null=False, blank=False)
    filename = models.CharField(max_length=255, blank=True, null=True)
    uplfile = models.FileField(max_length=255, blank=True, null=True)

    def get_folder_name(self):
        return for_ticket.get_files_folder()

    def createtime(self):
        return self.createdon.astimezone(pytz.timezone('America/New_York'))

    def get_internal_link_to_file(self):
        return reverse('get_ticket_file', kwargs={'ticketuuid': self.for_ticket.unid, 'filename': self.filename})

    def get_link_to_file(self):
        return settings.EMAIL_HOST_LINK + self.get_internal_link_to_file()
    
    def get_internal_link_to_view_file(self):
        return reverse('get_ticket_file_view', kwargs={'ticketuuid': self.for_ticket.unid, 'filename': self.filename})
    
    def get_link_to_view_file(self):
        return settings.EMAIL_HOST_LINK + self.get_internal_link_to_view_file()

    def get_file_name(self):
        return unquote(self.filename)

    def isimage(self):
        filename, extension=os.path.splitext(self.uplfile.name)
        return extension.lower() in settings.IMAGE_FILE_EXTENSIONS


class UploadedFileComment(models.Model):
    for_comment = models.ForeignKey(ticket_comment.TicketComment, on_delete=models.CASCADE, null=False, related_name="files")
    createdon = models.DateTimeField("Created time", auto_now_add=True, null=False, blank=False)
    filename = models.CharField(max_length=255, blank=True, null=True)
    uplfile = models.FileField(max_length=255, blank=True, null=True)

    def get_folder_name(self):
        return for_comment.get_files_folder()

    def createtime(self):
        return self.createdon.astimezone(pytz.timezone('America/New_York'))

    def get_internal_link_to_file(self):
        return reverse('get_comment_file', kwargs={'ticketuuid': self.for_comment.initial_ticket.unid, 'filename': self.filename, 'commentid': self.for_comment.id})

    def get_link_to_file(self):
        return settings.EMAIL_HOST_LINK + self.get_internal_link_to_file()
    
    def get_internal_link_to_view_file(self):
        return reverse('get_comment_file_view', kwargs={'ticketuuid': self.for_comment.initial_ticket.unid, 'filename': self.filename, 'commentid': self.for_comment.id})
    
    def get_link_to_view_file(self):
        return settings.EMAIL_HOST_LINK + self.get_internal_link_to_view_file()

    def get_file_name(self):
        return unquote(self.filename)

    def isimage(self):
        filename, extension=os.path.splitext(self.uplfile.name)
        return extension.lower() in settings.IMAGE_FILE_EXTENSIONS


def downloadFileFromTicket(request, ticketuuid, filename):
    try:
        tick = ticket.Ticket.objects.get(unid=ticketuuid)
    except Exception as exc:
        print(exc)
        return error_views.notfound(request)
    try:
        resfile = UploadedFileTicket.objects.get(for_ticket=tick, filename=filename)
    except Exception as exc:
        print(exc)
        return error_views.notfound(request)
    response = HttpResponse(resfile.uplfile.read())
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(os.path.basename(resfile.uplfile.name))
    response['X-Sendfile'] = smart_str(resfile.uplfile.name)
    return response


def viewFileFromTicket(request, ticketuuid, filename):
    try:
        tick = ticket.Ticket.objects.get(unid=ticketuuid)
    except Exception as exc:
        print(exc)
        return error_views.notfound(request)
    try:
        resfile = UploadedFileTicket.objects.get(for_ticket=tick, filename=filename)
    except Exception as exc:
        print(exc)
        return error_views.notfound(request)
    response = HttpResponse(resfile.uplfile.read(), 'image')
    return response


def downloadFileFromComment(request, ticketuuid, commentid, filename):
    try:
        comment = ticket_comment.TicketComment.objects.get(id=commentid)
        if comment.initial_ticket.unid != ticketuuid:
            return error_views.notfound(request)
    except Exception as exc:
        print(exc)
        return error_views.notfound(request)
    try:
        resfile = UploadedFileTicket.objects.get(for_ticket=comment, filename=filename)
    except Exception as exc:
        print(exc)
        return error_views.notfound(request)
    response = HttpResponse()
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(os.path.basename(resfile.uplfile.name))
    response['X-Sendfile'] = smart_str(resfile.uplfile.name)
    return response


def viewFileFromComment(request, ticketuuid, commentid, filename):
    try:
        comment = ticket_comment.TicketComment.objects.get(id=commentid)
        if comment.initial_ticket.unid != ticketuuid:
            return error_views.notfound(request)
    except Exception as exc:
        print(exc)
        return error_views.notfound(request)
    try:
        resfile = UploadedFileTicket.objects.get(for_ticket=comment, filename=filename)
    except Exception as exc:
        print(exc)
        return error_views.notfound(request)
    response = HttpResponse(resfile.uplfile.read(), 'image')
    return response


def save_file_ticket(ticket, ufile):
    path = ticket.get_files_folder()
    addition = ""
    filepath = os.path.join(path, addition, ufile.name)
    while os.path.exists(filepath):
        addition+=str(random.randint(0,9))
        filepath = os.path.join(path, addition, ufile.name)
    with default_storage.open(filepath, 'wb+') as destination:
        for chunk in ufile.chunks():
            destination.write(chunk)
    upf = UploadedFileTicket(for_ticket=ticket, uplfile=filepath, filename=quote(os.path.basename(filepath)))
    upf.save()
    return upf


def save_file_comment(comment, ufile):
    path = comment.get_files_folder()
    addition = ""
    filepath = os.path.join(path, addition, ufile.name)
    while os.path.exists(filepath):
        addition+=str(random.randint(0,9))
        filepath = os.path.join(path, addition, ufile.name)
    with default_storage.open(filepath, 'wb+') as destination:
        for chunk in ufile.chunks():
            destination.write(chunk)
    upf = UploadedFileComment(for_comment=comment, uplfile=filepath, filename=quote(os.path.basename(filepath)))
    upf.save()
    return upf
