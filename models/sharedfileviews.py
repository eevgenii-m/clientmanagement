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
from models.uploadlink import UploadLink, ClientUploadedFile
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


# ══════════════════════════════════════════════════════════════════
# UPLOAD LINKS
# ══════════════════════════════════════════════════════════════════

@login_required(login_url='login')
def all_upload_links(request):
    links = UploadLink.objects.filter(created_by=request.user).order_by('-created_on')
    return render(request, 'views/uploadlinks.html', {'links': links})


@login_required(login_url='login')
def create_upload_link(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        try:
            expires_days = min(max(1, int(request.POST.get('expires_days', 7))), 90)
        except (ValueError, TypeError):
            expires_days = 7
        try:
            max_files = min(max(1, int(request.POST.get('max_files', 10))), 50)
        except (ValueError, TypeError):
            max_files = 10
        if title:
            link = UploadLink.objects.create(
                title=title,
                description=description,
                expires_on=date.today() + timedelta(days=expires_days),
                max_files=max_files,
                created_by=request.user,
            )
            return redirect(reverse('view_upload_link', kwargs={'linkuuid': link.unid}))
    return render(request, 'views/createuploadlink.html', {})


@login_required(login_url='login')
def view_upload_link(request, linkuuid):
    link = get_object_or_404(UploadLink, unid=linkuuid)
    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'deactivate':
            link.is_active = False
            link.save()
        elif action == 'activate':
            link.is_active = True
            link.save()
        return redirect(reverse('view_upload_link', kwargs={'linkuuid': linkuuid}))
    files = link.uploaded_files.order_by('-uploaded_at')
    full_url = request.build_absolute_uri(
        reverse('client_upload_page', kwargs={'linkuuid': linkuuid})
    )
    return render(request, 'views/viewuploadlink.html', {
        'link': link,
        'files': files,
        'full_url': full_url,
    })


@login_required(login_url='login')
def delete_upload_link(request, linkuuid):
    link = get_object_or_404(UploadLink, unid=linkuuid)
    if request.method == 'POST':
        # Delete uploaded files from disk
        for cf in link.uploaded_files.all():
            try:
                cf.uplfile.delete(save=False)
            except Exception:
                pass
        link.delete()
    return redirect('all_upload_links')


@login_required(login_url='login')
def edit_upload_link(request, linkuuid):
    link = get_object_or_404(UploadLink, unid=linkuuid)
    if request.method == 'POST':
        title = request.POST.get('title', link.title).strip() or link.title
        link.title = title
        link.description = request.POST.get('description', '').strip()
        expires_days_raw = request.POST.get('expires_days', '').strip()
        if expires_days_raw:
            try:
                expires_days = min(max(1, int(expires_days_raw)), 90)
                link.expires_on = date.today() + timedelta(days=expires_days)
            except (ValueError, TypeError):
                pass
        try:
            max_files = min(max(1, int(request.POST.get('max_files', link.max_files))), 50)
            link.max_files = max_files
        except (ValueError, TypeError):
            pass
        link.save()
        return redirect(reverse('view_upload_link', kwargs={'linkuuid': linkuuid}))
    return render(request, 'views/edituploadlink.html', {'link': link})


def client_upload_page(request, linkuuid):
    link = get_object_or_404(UploadLink, unid=linkuuid)
    if not link.is_available():
        return render(request, 'views/uploadlinkexpired.html', {'link': link})
    error = None
    success = False
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        if not files:
            error = 'Please select at least one file.'
        elif link.uploaded_files.count() + len(files) > link.max_files:
            error = 'Too many files. Maximum %d files allowed for this link.' % link.max_files
        else:
            for ufile in files:
                cf = ClientUploadedFile(
                    upload_link=link,
                    original_filename=ufile.name,
                    ip_address=request.META.get('REMOTE_ADDR'),
                    file_size=ufile.size,
                )
                cf.uplfile = ufile
                cf.save()
            success = True
    return render(request, 'views/clientuploadpage.html', {
        'link': link,
        'error': error,
        'success': success,
    })
