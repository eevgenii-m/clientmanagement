from django import forms
from models import client
from clientmanagement import views as main_views
from django.urls import reverse
from django.shortcuts import render, redirect
from datetime import datetime
from phonenumber_field.formfields import PhoneNumberField
import collections, copy
from clientmanagement.widget import quill

class ClientForm(forms.ModelForm):
    phone = PhoneNumberField(label="Phone number", required=False, help_text="You can add the extension after an x")
    description = quill.QuillField(label='Additional information')
    order = ('name', 'address', 'phone', 'description')
    class Meta:
        model = client.Client
        fields = ('name', 'address', 'description')

    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)
        tmp = self.fields
        self.fields = collections.OrderedDict()
        for item in self.order:
            self.fields[item] = tmp[item]

        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            if (not instance.phone is None) and (instance.phone != ""):
                self.fields['phone'].initial = instance.phone.as_national

    def save(self, commit=True):
        client = super(ClientForm, self).save(commit=False)
        if ('phone' in self.changed_data):
            client.phone= self.cleaned_data["phone"]
        if commit:
            client.save()
        return client


def ClientFormParse(request):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    data={}
    if (request.method == 'POST') and ('action' in request.POST):
        if (request.POST['action']=='add'):
            form = ClientForm(request.POST)
            if form.is_valid():
                model = form.save(commit=False)
                model.save()
                return redirect(reverse('oneclient', kwargs={'clientid': model.id}))
            else:
                data['action'] = 'add'
                data['minititle'] = 'New Client'
                data['submbutton'] = 'Add client'
                data['PAGE_TITLE'] = 'New Client: CMS infotek'
                data['backurl'] = reverse('allclients')
        elif (request.POST['action']=='change'):
            if('targetid' in request.POST):
                try:
                    curcl=client.Client.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('allclients'))
                form = ClientForm(instance=curcl)
                data['action'] = 'changed'
                data['targetid'] = request.POST['targetid']
                data['minititle'] = 'Change Client "'+curcl.name+'"'
                data['submbutton'] = 'Change client'
                data['backurl'] = reverse('oneclient', kwargs={'clientid': curcl.id})
                data['deletebutton'] = 'Delete client'
            else:
                return redirect(reverse('allclients'))
        elif (request.POST['action']=='changed'):
            if('targetid' in request.POST):
                try:
                    curcl=client.Client.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('allclients'))
                form = ClientForm(request.POST, instance=curcl)
                if form.is_valid():
                    model = form.save(commit=False)
                    model.save()
                    return redirect(reverse('oneclient', kwargs={'clientid': model.id}))
                data['backurl'] = reverse('oneclient', kwargs={'clientid': curcl.id})
                data['action'] = 'changed'
                data['targetid'] = request.POST['targetid']
                data['minititle'] = 'Change Client "'+curcl.name+'"'
                data['submbutton'] = 'Change client'
                data['PAGE_TITLE'] = 'Change Client: CMS infotek'
            else:
                return redirect(reverse('allclients'))
        elif (request.POST['action']=='delete'):
            if('targetid' in request.POST):
                try:
                    curcl=client.Client.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('allclients'))
                curcl.delete()
                return redirect(reverse('allclients'))
            else:
                return redirect(reverse('allclients'))
        else:
            return redirect(reverse('allclients'))
    else:
        form = ClientForm()
        data['action']='add'
        data['minititle'] = 'New Client'
        data['submbutton'] = 'Add client'
        data['PAGE_TITLE'] = 'New Client: CMS infotek'
        data['backurl'] = reverse('allclients')
    data['form'] = form
    data['needquillinput'] = True
    data['built'] = datetime.now().strftime("%H:%M:%S")
    return render(request, 'forms/unimodelform.html', data, content_type='text/html')
