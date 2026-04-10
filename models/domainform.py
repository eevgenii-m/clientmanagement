from django import forms
from models import domain
from models import client
from clientmanagement import views as main_views
from django.urls import reverse
from django.shortcuts import render, redirect
from datetime import datetime

class DomainForm(forms.ModelForm):

    class Meta:
        model = domain.Domain
        fields = ('domainnameshort', 'domainnamelong', 'admin', 'dnsip', 'company', 'description')


def domainFormParse(request, clientid):    
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    data={}
    data['PAGE_TITLE'] = 'Change Domain: CMS infotek'
    try:
        b=client.Client.objects.get(id=clientid)
    except Exception as exc:
        return redirect(reverse('allclients'))
    if (request.method == 'POST') and ('action' in request.POST):
        if (request.POST['action']=='add'):
            form = DomainForm(request.POST)
            if not domain.checkUnique(b):
                return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
            if form.is_valid():
                model = form.save(commit=False)
                model.save()
                return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
            else:
                data['action']='add'
                data['minititle'] = 'Add Domain for '+b.name
                data['submbutton'] = 'Add domain'
                data['PAGE_TITLE'] = 'New Domain: CMS infotek'
        elif (request.POST['action']=='change'):
            try:
                curdomain = domain.getDomain(b)
            except Exception:
                return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
            form = DomainForm(instance=curdomain)
            data['action'] = 'changed'
            data['targetid'] = True
            data['deletebutton'] = 'Delete ' + curdomain.domainnameshort
            data['minititle'] = 'Change Domain "'+curdomain.domainnameshort+'"'
            data['submbutton'] = 'Change domain'
        elif (request.POST['action']=='changed'):
            try:
                curdomain = domain.getDomain(b)
            except Exception:
                return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
            form = DomainForm(request.POST, instance=curdomain)
            if form.is_valid():
                model = form.save(commit=False)
                model.save()
                return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
            data['action'] = 'changed'
            data['targetid'] = True
            data['deletebutton'] = 'Delete ' + curdomain.domainnameshort
            data['minititle'] = 'Change Router for "'+b.name+'"'
            data['submbutton'] = 'Change domain'
        elif (request.POST['action']=='delete'):
            try:
                curdomain = domain.getDomain(b)
            except Exception:
                return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
            curdomain.delete()
            return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
        else:
            return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
    else:
        form = DomainForm(initial={'company': b})
        data['action']='add'
        data['PAGE_TITLE'] = 'New Domain: CMS infotek'
        data['minititle'] = 'Add Domain for '+b.name
        data['submbutton'] = 'Add domain'
    data['form'] = form
    data['built'] = datetime.now().strftime("%H:%M:%S") 
    data['backurl'] = reverse('oneclient', kwargs={'clientid': clientid})
    return render(request, 'forms/unimodelform.html', data, content_type='text/html')
