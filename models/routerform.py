from django import forms
from models import router
from models import client
from clientmanagement import views as main_views
from clientmanagement.widget import clear_file_input
from django.urls import reverse
from django.shortcuts import render, redirect
from datetime import datetime
import os, pytz

class RouterForm(forms.ModelForm):

    class Meta:
        model = router.Router
        fields = ('manufacturer', 'model', 'serialnumber', 'firmwareversion', 'settingslink', 'externalip',
                'connection_type', 'ip_type', 'ip_address', 'mac_address', 'company', 'settings_file', 'description')
        widgets = {
            'settings_file': clear_file_input.ClearFileInput,
        }    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            if 'settings_file' in self.changed_data:
                if not instance.settings_file is None:
                    try:
                        instance.settings_file.delete()
                    except Exception as a:
                        pass
            if instance.settings_file is not None and instance.settings_file_uploaded is not None:
                self.fields['settings_file'].widget.add_to_filename = instance.uploaded_on_text()


    def save(self, commit=True):
        model = super().save(commit=False)
        if 'settings_file' in self.changed_data:
            model.settings_file_uploaded = datetime.now(pytz.utc)
        if commit:
            model.save()
        return model



def routerFormParse(request, clientid):    
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    data={}
    data['PAGE_TITLE'] = 'Change Router: CMS infotek'
    try:
        b=client.Client.objects.get(id=clientid)
    except Exception as exc:
        return redirect(reverse('allclients'))
    if (request.method == 'POST') and ('action' in request.POST):
        if (request.POST['action']=='add'):
            form = RouterForm(request.POST, request.FILES)
            if not router.checkUnique(b):
                return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
            if form.is_valid():
                model = form.save(commit=False)
                model.save()
                return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
            else:
                data['action']='add'
                data['PAGE_TITLE'] = 'New Router: CMS infotek'
                data['minititle'] = 'Add Router for '+b.name
                data['submbutton'] = 'Add router'
        elif (request.POST['action']=='change'):
            try:
                currouter = router.getRouter(b)
            except Exception:
                return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
            form = RouterForm(instance=currouter)
            data['action'] = 'changed'
            data['targetid'] = True
            data['deletebutton'] = 'Delete router for ' + b.name
            data['minititle'] = 'Change Router for "'+b.name+'"'
            data['submbutton'] = 'Change router'
        elif (request.POST['action']=='changed'):
            try:
                currouter = router.getRouter(b)
            except Exception:
                return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
            form = RouterForm(request.POST, request.FILES, instance=currouter)
            if form.is_valid():
                model = form.save(commit=False)
                model.save()
                return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
            data['action'] = 'changed'
            data['targetid'] = True
            data['deletebutton'] = 'Delete router for ' + b.name
            data['minititle'] = 'Change Router for "'+b.name+'"'
            data['submbutton'] = 'Change router'
        elif (request.POST['action']=='delete'):
            try:
                currouter = router.getRouter(b)
            except Exception:
                return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
            currouter.delete()
            return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
        else:
            return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
    else:
        form = RouterForm(initial={'company': b})
        data['action']='add'
        data['PAGE_TITLE'] = 'New Router: CMS infotek'
        data['minititle'] = 'Add Router for '+b.name
        data['submbutton'] = 'Add router'
    data['form'] = form
    data['built'] = datetime.now().strftime("%H:%M:%S") 
    data['backurl'] = reverse('oneclient', kwargs={'clientid': clientid})
    return render(request, 'forms/unimodelform.html', data, content_type='text/html')
