from django import forms
from models import person
from models import computers
from models import client
from django.urls import reverse
from django.shortcuts import render, redirect
from datetime import datetime
from phonenumber_field.formfields import PhoneNumberField
import collections, copy

class PersonForm(forms.ModelForm):
    phone = PhoneNumberField(label="Phone number", required=False, help_text="You can add the extension after an x")
    order=('firstname', 'lastname', 'email', 'phone', 'annoyance', 'employedby', 'description')
    class Meta:
        model = person.Person
        fields = ('firstname', 'lastname', 'email', 'annoyance', 'employedby', 'description')

    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)
        tmp = self.fields
        self.fields = collections.OrderedDict()
        for item in self.order:
            self.fields[item] = tmp[item]

        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            if (not instance.phone is None) and (instance.phone != ""):
                self.fields['phone'].initial = instance.phone.as_national

    def save(self, commit=True):
        person = super(PersonForm, self).save(commit=False)
        if ('phone' in self.changed_data):
            person.phone= self.cleaned_data["phone"]
        if commit:
            person.save()
        return person


# class PersonFullForm(PersonForm): 

#     class Meta(PersonForm.Meta):
#         fields = ('firstname', 'lastname', 'email', 'phone', 'annoyance', 'employedby', 'description')
 

def personFormParse(request, clientid):
    data={}
    data['PAGE_TITLE'] = 'Change Person: CMS infotek'
    try:
        b=client.Client.objects.get(id=clientid)
    except Exception as exc:
        return redirect(reverse('allclients'))
    if (request.method == 'POST') and ('action' in request.POST):
        if (request.POST['action']=='add'):
            form = PersonForm(request.POST)
            if form.is_valid():
                model = form.save(commit=False)
                model.save()
                return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
            else:
                data['action']='add'
                data['PAGE_TITLE'] = 'New Person: CMS infotek'
                data['minititle'] = 'Add Person'
                data['submbutton'] = 'Add person'
        elif (request.POST['action']=='change'):
            if('targetid' in request.POST):
                try:
                    curpers=person.Person.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
                form = PersonForm(instance=curpers)
                data['action'] = 'changed'
                data['targetid'] = request.POST['targetid']
                data['minititle'] = 'Change Person "'+curpers.name()+'"'
                data['submbutton'] = 'Change person'
                data['deletebutton'] = 'Delete ' +curpers.name()
            else:
                return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
        elif (request.POST['action']=='changed'):
            if('targetid' in request.POST):
                try:
                    curpers=person.Person.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
                form = PersonForm(request.POST, instance=curpers)
                if form.is_valid():
                    model = form.save(commit=False)
                    model.save()
                    return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
                data['action'] = 'changed'
                data['targetid'] = request.POST['targetid']
                data['minititle'] = 'Change Person "'+curpers.name()+'"'
                data['submbutton'] = 'Change person'
                data['deletebutton'] = 'Delete ' +curpers.name()
            else:
                return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
        elif (request.POST['action']=='delete'):
            if('targetid' in request.POST):
                try:
                    curpers=person.Person.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
                curpers.delete()
                return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
            else:
                return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
        else:
            return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
    else:
        form = PersonForm(initial={'employedby': b})
        data['action']='add'
        data['PAGE_TITLE'] = 'New Person: CMS infotek'
        data['minititle'] = 'Add Person'
        data['submbutton'] = 'Add person'
    data['form'] = form
    data['built'] = datetime.now().strftime("%H:%M:%S") 
    data['backurl'] = reverse('oneclient', kwargs={'clientid': clientid})
    return render(request, 'forms/unimodelform.html', data, content_type='text/html')
