from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import FileResponse
from django.utils.encoding import smart_str
from datetime import datetime, date, timedelta
import os, mimetypes

from models import sharedfile
from models.filedownloadlog import FileDownloadLog
from clientmanagement import views as main_views


class SharedFileForm(forms.ModelForm):
    expires_days = forms.IntegerField(
        required=False,
        label='Expires in (days)',
        help_text='Default 7 days, maximum 90 days. Leave blank for no expiry.',
        widget=forms.NumberInput(attrs={'min': 1, 'max': 90, 'placeholder': '7'}),
    )
    max_downloads = forms.IntegerField(
        required=False,
        label='Download limit (optional)',
        help_text='Leave blank for unlimited downloads.',
        widget=forms.NumberInput(attrs={'min': 1, 'placeholder': 'Unlimited'}),
    )

    field_order = ['uplfile', 'description', 'expires_days', 'max_downloads']

    class Meta:
        model = sharedfile.SharedFile
        fields = ('uplfile', 'description')
        labels = {
            'uplfile': 'File',
            'description': 'Description (optional)',
        }


@login_required(login_url='login')
def AllSharedFilesParser(request):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    files = sharedfile.SharedFile.objects.all().order_by('-createdon')
    data = {
        'PAGE_TITLE': 'Shared Files: CMS infotek',
        'files': files,
        'needdatatables': True,
        'built': datetime.now().strftime("%H:%M:%S"),
    }
    return render(request, 'views/allfiles.html', data, content_type='text/html')


@login_required(login_url='login')
def UploadSharedFileParser(request):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    if request.method == 'POST':
        form = SharedFileForm(request.POST, request.FILES)
        if form.is_valid():
            sf = form.save(commit=False)
            sf.uploaded_by = request.user
            if request.FILES.get('uplfile'):
                sf.original_filename = request.FILES['uplfile'].name
            expires_days = form.cleaned_data.get('expires_days')
            if expires_days:
                expires_days = min(max(1, int(expires_days)), 90)
                sf.expireon = date.today() + timedelta(days=expires_days)
            max_dl = form.cleaned_data.get('max_downloads')
            if max_dl:
                sf.max_downloads = max_dl
            sf.save()
            return redirect(reverse('all_shared_files'))
    else:
        form = SharedFileForm()
    data = {
        'PAGE_TITLE': 'Upload File: CMS infotek',
        'form': form,
        'built': datetime.now().strftime("%H:%M:%S"),
    }
    return render(request, 'views/uploadfile.html', data, content_type='text/html')


def DownloadSharedFilePublic(request, fileuuid):
    try:
        sf = sharedfile.SharedFile.objects.get(unid=fileuuid)
    except sharedfile.SharedFile.DoesNotExist:
        return render(request, 'views/fileexpired.html', {'reason': 'not_found'},
                      content_type='text/html')
    if sf.is_expired():
        return render(request, 'views/fileexpired.html', {'reason': 'expired'},
                      content_type='text/html')
    if sf.is_download_limit_reached():
        return render(request, 'views/fileexpired.html', {'reason': 'limit_reached'},
                      content_type='text/html')
    try:
        file_path = sf.uplfile.path
        if not os.path.exists(file_path):
            return render(request, 'views/fileexpired.html', {'reason': 'not_found'},
                          content_type='text/html')
        sf.downloads += 1
        sf.save(update_fields=['downloads'])
        FileDownloadLog.objects.create(
            shared_file=sf,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            referer=request.META.get('HTTP_REFERER', '')[:500],
        )
        filename = sf.filename_display()
        content_type, _ = mimetypes.guess_type(filename)
        if content_type is None:
            content_type = 'application/octet-stream'
        response = FileResponse(open(file_path, 'rb'), content_type=content_type)
        response['Content-Disposition'] = 'attachment; filename="%s"' % smart_str(filename)
        return response
    except Exception:
        return render(request, 'views/fileexpired.html', {'reason': 'error'},
                      content_type='text/html')


@login_required(login_url='login')
def DeleteSharedFileView(request, fileid):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    if request.method == 'POST':
        try:
            sf = sharedfile.SharedFile.objects.get(id=fileid)
            try:
                sf.uplfile.delete(save=False)
            except Exception:
                pass
            sf.delete()
        except sharedfile.SharedFile.DoesNotExist:
            pass
    return redirect(reverse('all_shared_files'))


@login_required(login_url='login')
def ViewSharedFile(request, fileuuid):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    sf = get_object_or_404(sharedfile.SharedFile, unid=fileuuid)
    logs = sf.download_logs.order_by('-downloaded_at')[:50]
    data = {
        'PAGE_TITLE': sf.filename_display() + ': CMS infotek',
        'file': sf,
        'logs': logs,
        'built': datetime.now().strftime("%H:%M:%S"),
    }
    return render(request, 'views/fileview.html', data, content_type='text/html')


@login_required(login_url='login')
def EditSharedFile(request, fileuuid):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    sf = get_object_or_404(sharedfile.SharedFile, unid=fileuuid)
    if request.method == 'POST':
        sf.description = request.POST.get('description', sf.description or '').strip() or None
        expires_days_raw = request.POST.get('expires_days', '').strip()
        if expires_days_raw:
            try:
                expires_days = min(max(1, int(expires_days_raw)), 90)
                sf.expireon = date.today() + timedelta(days=expires_days)
            except ValueError:
                pass
        else:
            sf.expireon = None
        max_dl_raw = request.POST.get('max_downloads', '').strip()
        sf.max_downloads = int(max_dl_raw) if max_dl_raw else None
        sf.save()
        return redirect(reverse('shared_file_view', kwargs={'fileuuid': sf.unid}))
    days_remaining = sf.days_left()
    data = {
        'PAGE_TITLE': 'Edit File: CMS infotek',
        'file': sf,
        'days_remaining': days_remaining if days_remaining is not None else '',
        'built': datetime.now().strftime("%H:%M:%S"),
    }
    return render(request, 'views/editfile.html', data, content_type='text/html')
