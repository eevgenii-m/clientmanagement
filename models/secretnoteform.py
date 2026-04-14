from django import forms
from models import secretnote
from clientmanagement import views as main_views, modelgetters, error_views
from django.urls import reverse
from django.shortcuts import render, redirect
from datetime import datetime, timedelta
import collections, copy


class SecretNoteForm(forms.ModelForm):
    note_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 10, 'style': 'resize: vertical;'}),
        label="Secret note text",
        required=False,
    )
    order = ('contactemail', 'reads_max', 'expireon', 'subject', 'note_text')
    class Meta:
        model = secretnote.SecretNote
        fields = ('contactemail', 'reads_max', 'expireon', 'subject', 'note_text')
        widgets = {
            'expireon': forms.SelectDateWidget,
        }

    def __init__(self, *args, **kwargs):
        super(SecretNoteForm, self).__init__(*args, **kwargs)
        tmp = self.fields
        self.fields = collections.OrderedDict()
        for item in self.order:
            self.fields[item] = tmp[item]

    def save(self, commit=True):
        note = super(SecretNoteForm, self).save(commit=False)
        return note


def SecretNoteFormParse(request):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    data={}
    if (request.method == 'POST') and ('action' in request.POST):
        if (request.POST['action']=='add'):
            form = SecretNoteForm(request.POST)
            if form.is_valid():
                model = form.save(commit=False)
                model.save()
                return redirect(reverse('note_internal', kwargs={'noteid': model.id}))
            else:
                data['action'] = 'add'
                data['minititle'] = 'New Secret Note'
                data['submbutton'] = 'Add Note'
                data['PAGE_TITLE'] = 'New Note: CMS infotek'
                data['backurl'] = reverse('all_notes')
        elif (request.POST['action']=='change'):
            if('targetid' in request.POST):
                try:
                    curnote=secretnote.SecretNote.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('all_notes'))
                form = SecretNoteForm(instance=curnote)
                data['action'] = 'changed'
                data['targetid'] = request.POST['targetid']
                data['minititle'] = 'Change Note'
                data['submbutton'] = 'Change note'
                data['backurl'] = reverse('note_internal', kwargs={'noteid': curnote.id})
                data['deletebutton'] = 'Delete note'
            else:
                return redirect(reverse('all_notes'))
        elif (request.POST['action']=='changed'):
            if('targetid' in request.POST):
                try:
                    curnote=secretnote.SecretNote.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('all_notes'))
                form = SecretNoteForm(request.POST, instance=curnote)
                if form.is_valid():
                    model = form.save(commit=False)
                    model.save()
                    return redirect(reverse('note_internal', kwargs={'noteid': model.id}))
                data['backurl'] = reverse('note_internal', kwargs={'noteid': curnote.id})
                data['action'] = 'changed'
                data['targetid'] = request.POST['targetid']
                data['minititle'] = 'Change Note'
                data['submbutton'] = 'Change note'
                data['backurl'] = reverse('note_internal', kwargs={'noteid': curnote.id})
                data['deletebutton'] = 'Delete note'
            else:
                return redirect(reverse('all_notes'))
        elif (request.POST['action']=='delete'):
            if('targetid' in request.POST):
                try:
                    curnote=secretnote.SecretNote.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('all_notes'))
                curnote.delete()
                return redirect(reverse('all_notes'))
            else:
                return redirect(reverse('all_notes'))
        else:
            return redirect(reverse('all_notes'))
    else:
        form = SecretNoteForm()
        data['action'] = 'add'
        data['minititle'] = 'New Secret Note'
        data['submbutton'] = 'Add Note'
        data['PAGE_TITLE'] = 'New Note: CMS infotek'
        data['backurl'] = reverse('all_notes')
    data['form'] = form
    data['built'] = datetime.now().strftime("%H:%M:%S")
    data['needeasymde'] = True
    return render(request, 'forms/unimodelform.html', data, content_type='text/html')


def AllSecretNotes(request, reqtype):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    data = modelgetters.form_all_notes_data()
    if data is None:
        data = {}
    show_available = reqtype == '' or reqtype == 'a'
    show_unavailable = reqtype == 'u' or reqtype == 'a'
    data['needdatatables'] = True
    data['PAGE_TITLE'] = 'Secret Notes: CMS infotek'
    data['built'] = datetime.now().strftime("%H:%M:%S")
    data['show_available'] = show_available
    data['show_unavailable'] = show_unavailable
    return render(request, 'views/allsecretnotes.html', data, content_type='text/html')


def SecretNoteViewInternal(request, noteid):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    data = modelgetters.form_one_note_data_internal(noteid)
    if data is None:
        return error_views.notfound(request)
    data['PAGE_TITLE'] = 'Secret Note: CMS infotek'
    data['built'] = datetime.now().strftime("%H:%M:%S")
    data['needquillinput'] = True   # keep for backward-compat display of legacy Quill notes
    return render(request, 'views/secretnoteinternal.html', data, content_type='text/html')


def SecretNoteViewExternalClose(request, noteuuid):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    data = modelgetters.form_one_note_data_external(noteuuid)
    if data is None:
        return error_views.notfound(request)
    data['PAGE_TITLE'] = 'Secret Note: CMS infotek'
    data['built'] = datetime.now().strftime("%H:%M:%S")
    # Quill CSS/JS loaded conditionally in the template based on note content type
    return render(request, 'views/secretnoteclose.html', data, content_type='text/html')


def SecretNoteViewExternalOpen(request, noteuuid):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    data = modelgetters.form_one_note_data_external(noteuuid)
    if data is None:
        return error_views.notfound(request)
    data['PAGE_TITLE'] = 'Secret Note: CMS infotek'
    data['built'] = datetime.now().strftime("%H:%M:%S")
    return render(request, 'views/secretnoteopen.html', data, content_type='text/html')
