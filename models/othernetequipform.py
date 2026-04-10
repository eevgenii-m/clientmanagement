from django import forms
from models import othernetequip
from models import client
from clientmanagement import views as main_views
from django.urls import reverse
from django.shortcuts import render, redirect
from datetime import datetime

class OtherNetworkEquipmentForm(forms.ModelForm):

    class Meta:
        model = othernetequip.OtherNetworkEquipment
        fields = ('equipmenttype', 'manufacturer', 'model', 'serialnumber', 'connection_type', 'ip_type', 'ip_address', 'mac_address', 'company', 'description')

class OtherNetworkEquipmentFullForm(forms.ModelForm):

    class Meta:
        model = othernetequip.OtherNetworkEquipment
        fields = ('equipmenttype', 'manufacturer', 'model', 'serialnumber', 'connection_type', 'ip_type', 'ip_address', 'mac_address', 'company', 'description')


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # if 'instance' in kwargs:
        #     self.fields['user'].queryset = kwargs['instance'].company.employees.all().order_by('firstname', 'lastname')


def otherNetEquipFormParse(request, clientid):    
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    data={}
    data['PAGE_TITLE'] = 'Change Network Equipment: CMS infotek'
    try:
        b=client.Client.objects.get(id=clientid)
    except Exception as exc:
        return redirect(reverse('allclients'))
    if (request.method == 'POST') and ('action' in request.POST):
        if (request.POST['action']=='add'):
            form = OtherNetworkEquipmentForm(request.POST)
            if form.is_valid():
                model = form.save(commit=False)
                model.save()
                return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
            else:
                data['action']='add'
                data['PAGE_TITLE'] = 'New Network Equipment: CMS infotek'
                data['minititle'] = 'Add Network Equipment'
                data['submbutton'] = 'Add network equipment'
        elif (request.POST['action']=='change'):
            if('targetid' in request.POST):
                try:
                    curequip=othernetequip.OtherNetworkEquipment.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
                form = OtherNetworkEquipmentFullForm(instance=curequip)
                data['action'] = 'changed'
                data['targetid'] = request.POST['targetid']
                data['minititle'] = 'Change Network Equipment "'+curequip.equipmenttype+'"'
                data['submbutton'] = 'Change network equipment'
                data['deletebutton'] = 'Delete ' + curequip.equipmenttype
            else:
                return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
        elif (request.POST['action']=='changed'):
            if('targetid' in request.POST):
                try:
                    curequip=othernetequip.OtherNetworkEquipment.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
                form = OtherNetworkEquipmentFullForm(instance=curequip)
                if form.is_valid():
                    model = form.save(commit=False)
                    model.save()
                    return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
                form = OtherNetworkEquipmentFullForm(instance=curequip)
                data['action'] = 'changed'
                data['targetid'] = request.POST['targetid']
                data['minititle'] = 'Change Network Equipment "'+curequip.equipmenttype+'"'
                data['submbutton'] = 'Change network equipment'
                data['deletebutton'] = 'Delete ' + curequip.equipmenttype
            else:
                return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
        elif (request.POST['action']=='delete'):
            if('targetid' in request.POST):
                try:
                    curequip=othernetequip.OtherNetworkEquipment.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
                curequip.delete()
                return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
            else:
                return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
        else:
            return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
    else:
        form = OtherNetworkEquipmentForm(initial={'company': b})
        data['action']='add'
        data['PAGE_TITLE'] = 'New Network Equipment: CMS infotek'
        data['minititle'] = 'Add Network Equipment'
        data['submbutton'] = 'Add network equipment'
    data['form'] = form
    data['built'] = datetime.now().strftime("%H:%M:%S") 
    data['backurl'] = reverse('oneclient', kwargs={'clientid': clientid})
    return render(request, 'forms/unimodelform.html', data, content_type='text/html')
