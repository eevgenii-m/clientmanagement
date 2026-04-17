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
    order=('firstname', 'lastname', 'email', 'phone', 'employedby', 'description')
    class Meta:
        model = person.Person
        fields = ('firstname', 'lastname', 'email', 'employedby', 'description')

    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)
        tmp = self.fields
        self.fields = collections.OrderedDict()
        for item in self.order:
            self.fields[item] = tmp[item]

        self.fields['employedby'].required = False

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
 

def personFormParse(request, clientid=None):
    """Handle add/edit/delete for a person.

    Works with or without a client context:
      - clientid=None  -> standalone (People page), back to allpeople
      - clientid=<id>  -> client-scoped, back to that client's detail page
    """
    data = {}
    data['PAGE_TITLE'] = 'Change Person: CMS infotek'

    # Resolve client and back URL
    if clientid is not None:
        try:
            b = client.Client.objects.get(id=clientid)
        except Exception:
            return redirect(reverse('allclients'))
        back_url = reverse('oneclient', kwargs={'clientid': clientid})
    else:
        b = None
        back_url = reverse('allpeople')

    if (request.method == 'POST') and ('action' in request.POST):
        if (request.POST['action'] == 'add'):
            form = PersonForm(request.POST)
            if form.is_valid():
                model = form.save(commit=False)
                model.save()
                return redirect(back_url)
            else:
                data['action'] = 'add'
                data['PAGE_TITLE'] = 'New Person: CMS infotek'
                data['minititle'] = 'Add Person'
                data['submbutton'] = 'Add person'
        elif (request.POST['action'] == 'change'):
            if 'targetid' in request.POST:
                try:
                    curpers = person.Person.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(back_url)
                form = PersonForm(instance=curpers)
                data['action'] = 'changed'
                data['targetid'] = request.POST['targetid']
                data['minititle'] = 'Change Person "' + curpers.name() + '"'
                data['submbutton'] = 'Change person'
            else:
                return redirect(back_url)
        elif (request.POST['action'] == 'changed'):
            if 'targetid' in request.POST:
                try:
                    curpers = person.Person.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(back_url)
                form = PersonForm(request.POST, instance=curpers)
                if form.is_valid():
                    model = form.save(commit=False)
                    model.save()
                    return redirect(back_url)
                data['action'] = 'changed'
                data['targetid'] = request.POST['targetid']
                data['minititle'] = 'Change Person "' + curpers.name() + '"'
                data['submbutton'] = 'Change person'
            else:
                return redirect(back_url)
        elif (request.POST['action'] == 'delete'):
            if 'targetid' in request.POST:
                try:
                    curpers = person.Person.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(back_url)
                curpers.delete()
                return redirect(back_url)
            else:
                return redirect(back_url)
        else:
            return redirect(back_url)
    else:
        initial = {'employedby': b} if b else {}
        form = PersonForm(initial=initial)
        data['action'] = 'add'
        data['PAGE_TITLE'] = 'New Person: CMS infotek'
        data['minititle'] = 'Add Person'
        data['submbutton'] = 'Add person'

    data['form'] = form
    data['built'] = datetime.now().strftime("%H:%M:%S")
    data['backurl'] = back_url
    return render(request, 'forms/unimodelform.html', data, content_type='text/html')
