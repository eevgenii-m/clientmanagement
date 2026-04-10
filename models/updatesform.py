from django import forms
from clientmanagement import views as main_views
from django.urls import reverse
from django.shortcuts import render, redirect
from datetime import datetime
from models import updates
from clientmanagement.widget import quill
import pytz

class SystemUpdateForm(forms.ModelForm):
    newstext = quill.QuillField(label="Update text*")
    class Meta:
        model = updates.SystemUpdates
        fields = ('version', 'postedon', 'tittle', 'newstext')
        # widgets = {
        #     'postedon':  forms.SplitDateTimeWidget
        # }


def SystemUpdateFormParse(request):    
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    data={}
    data['PAGE_TITLE'] = 'Change posted update: CMS infotek'
    if (request.method == 'POST') and ('action' in request.POST):
        if (request.POST['action']=='add'):
            form = SystemUpdateForm(request.POST)
            if form.is_valid():
                model = form.save(commit=False)
                model.author = request.user.get_full_name()
                model.save()
                return redirect(reverse('updates'))
            else:
                data['action']='add'
                data['PAGE_TITLE'] = 'Post an update: CMS infotek'
                data['minitittle'] = 'Post Update'
                data['submbutton'] = 'Post Update'
        elif (request.POST['action']=='change'):
            if('targetid' in request.POST):
                try:
                    curpost=updates.SystemUpdates.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('updates'))
                if not curpost.editable():
                    return redirect(reverse('updates'))
                else:
                    curpost.createdon = datetime.now(pytz.utc)
                    curpost.save()
                form = SystemUpdateForm(instance=curpost)
                data['action'] = 'changed'
                data['targetid'] = request.POST['targetid']
                data['PAGE_TITLE'] = 'Post an update: CMS infotek'
                data['minitittle'] = 'Change Posted Update'
                data['submbutton'] = 'Change posted update'
                data['deletebutton'] = 'Delete post'
            else:
                curpost=updates.SystemUpdates.objects.get(id=request.POST['targetid'])
        elif (request.POST['action']=='changed'):
            if('targetid' in request.POST):
                try:
                    curpost=updates.SystemUpdates.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('updates'))
                if not curpost.editable():
                    return redirect(reverse('updates'))
                form = SystemUpdateForm(request.POST, instance=curpost)
                if form.is_valid():
                    model = form.save(commit=False)
                    model.createdon = datetime.now(pytz.utc)
                    model.save()
                    return redirect(reverse('updates'))                    
                curpost.createdon = datetime.now(pytz.utc)
                curpost.save()
                data['action'] = 'changed'
                data['targetid'] = request.POST['targetid']
                data['PAGE_TITLE'] = 'Post an update: CMS infotek'
                data['minitittle'] = 'Change Posted Update'
                data['submbutton'] = 'Change posted update'
                data['deletebutton'] = 'Delete post'
            else:
                return redirect(reverse('updates'))
        elif (request.POST['action']=='send'):
            if('targetid' in request.POST):
                try:
                    curpost=updates.SystemUpdates.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('updates'))
                if (not curpost.wassent):
                    curpost.sendemail()
                return redirect(reverse('updates'))
        elif (request.POST['action']=='delete'): 
            if('targetid' in request.POST):
                try:
                    curpost=updates.SystemUpdates.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('updates'))
                curpost.delete()
                return redirect(reverse('updates'))
            else:
                return redirect(reverse('updates'))
        else:
            return redirect(reverse('updates'))
    else:
        form = SystemUpdateForm(initial={'version': updates.getCurrentVersion()})
        data['action']='add'
        data['PAGE_TITLE'] = 'Post Update: CMS infotek'
        data['minitittle'] = 'Post Update'
        data['submbutton'] = 'Post update'
    data['form'] = form
    data['built'] = datetime.now().strftime("%H:%M:%S") 
    data['backurl'] = reverse('updates')
    data['needquillinput'] = True
    return render(request, 'forms/unimodelform.html', data, content_type='text/html')
