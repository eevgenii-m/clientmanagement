from django import forms
from models import computers
from models import client
from clientmanagement import views as main_views
from django.urls import reverse
from django.shortcuts import render, redirect
from datetime import datetime

class ComputerForm(forms.ModelForm):

    class Meta:
        model = computers.Computer
        fields = ('computername', 'operatingsystem', 'compmonth', 'compyear', 'manufacturer', 'model', 'serialnumber', 'connection_type', 'ip_type', 'ip_address', 'mac_address', 'company', 'description')

class ComputerFullForm(forms.ModelForm):

    class Meta:
        model = computers.Computer
        fields = ('computername', 'operatingsystem', 'compmonth', 'compyear', 'manufacturer', 'model', 'serialnumber', 'connection_type', 'ip_type', 'ip_address', 'mac_address', 'company', 'description')


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # if 'instance' in kwargs:
        #     self.fields['user'].queryset = kwargs['instance'].company.employees.all().order_by('firstname', 'lastname')


def computerFormParse(request, clientid):    
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    data={}
    data['PAGE_TITLE'] = 'Change Computer: CMS infotek'
    try:
        b=client.Client.objects.get(id=clientid)
    except Exception as exc:
        return redirect(reverse('allclients'))
    if (request.method == 'POST') and ('action' in request.POST):
        if (request.POST['action']=='add'):
            form = ComputerForm(request.POST)
            if form.is_valid():
                model = form.save(commit=False)
                model.save()
                return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
            else:
                data['action']='add'
                data['PAGE_TITLE'] = 'New Computer: CMS infotek'
                data['minititle'] = 'Add computer'
                data['submbutton'] = 'Add computer'
        elif (request.POST['action']=='change'):
            if('targetid' in request.POST):
                try:
                    curcomp=computers.Computer.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
                form = ComputerFullForm(instance=curcomp)
                data['action'] = 'changed'
                data['targetid'] = request.POST['targetid']
                data['minititle'] = 'Change Computer "'+curcomp.computername+'"'
                data['submbutton'] = 'Change computer'
                data['deletebutton'] = 'Delete ' +curcomp.computername
            else:
                return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
        elif (request.POST['action']=='changed'):
            if('targetid' in request.POST):
                try:
                    curcomp=computers.Computer.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
                form = ComputerFullForm(request.POST, instance=curcomp)
                if form.is_valid():
                    model = form.save(commit=False)
                    model.save()
                    return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
                data['action'] = 'changed'
                data['targetid'] = request.POST['targetid']
                data['minititle'] = 'Change Computer "'+curcomp.computername+'"'
                data['submbutton'] = 'Change computer'
                data['deletebutton'] = 'Delete ' +curcomp.computername
            else:
                return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
        elif (request.POST['action']=='delete'):
            if('targetid' in request.POST):
                try:
                    curcomp=computers.Computer.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
                curcomp.delete()
                return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
            else:
                return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
        else:
            return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
    else:
        form = ComputerForm(initial={'company': b})
        data['action']='add'
        data['PAGE_TITLE'] = 'New Computer: CMS infotek'
        data['minititle'] = 'Add computer'
        data['submbutton'] = 'Add computer'
    data['form'] = form
    data['backurl'] = reverse('oneclient', kwargs={'clientid': clientid})
    data['built'] = datetime.now().strftime("%H:%M:%S") 
    return render(request, 'forms/unimodelform.html', data, content_type='text/html')
