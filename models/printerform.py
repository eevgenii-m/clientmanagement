from django import forms
from models import printer
from models import client
from clientmanagement import views as main_views
from django.urls import reverse
from django.shortcuts import render, redirect
from datetime import datetime

class PrinterForm(forms.ModelForm):

    class Meta:
        model = printer.Printer
        fields = ('printername', 'prmonth', 'pryear', 'printertype', 'manufacturer', 'model', 'serialnumber', 'connection_type', 'ip_type', 'ip_address', 'mac_address', 'company', 'description')

class PrinterFullForm(forms.ModelForm):

    class Meta:
        model = printer.Printer
        fields = ('printername', 'prmonth', 'pryear', 'printertype', 'manufacturer', 'model', 'serialnumber', 'connection_type', 'ip_type', 'ip_address', 'mac_address', 'company', 'description')


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # if 'instance' in kwargs:
        #     self.fields['user'].queryset = kwargs['instance'].company.employees.all().order_by('firstname', 'lastname')


def printerFormParse(request, clientid):    
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    data={}
    data['PAGE_TITLE'] = 'Change Printer: CMS infotek'
    try:
        b=client.Client.objects.get(id=clientid)
    except Exception as exc:
        return redirect(reverse('allclients'))
    if (request.method == 'POST') and ('action' in request.POST):
        if (request.POST['action']=='add'):
            form = PrinterForm(request.POST)
            if form.is_valid():
                model = form.save(commit=False)
                model.save()
                return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
            else:
                data['action']='add'
                data['PAGE_TITLE'] = 'New Printer: CMS infotek'
                data['minititle'] = 'Add printer'
                data['submbutton'] = 'Add printer'
        elif (request.POST['action']=='change'):
            if('targetid' in request.POST):
                try:
                    curprinter=printer.Printer.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
                form = PrinterFullForm(instance=curprinter)
                data['action'] = 'changed'
                data['targetid'] = request.POST['targetid']
                data['minititle'] = 'Change Printer "'+curprinter.printername+'"'
                data['submbutton'] = 'Change printer'
                data['deletebutton'] = 'Delete ' +curprinter.printername
            else:
                return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
        elif (request.POST['action']=='changed'):
            if('targetid' in request.POST):
                try:
                    curprinter=printer.Printer.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
                form = PrinterFullForm(request.POST, instance=curprinter)
                if form.is_valid():
                    model = form.save(commit=False)
                    model.save()
                    return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
                data['action'] = 'changed'
                data['targetid'] = request.POST['targetid']
                data['minititle'] = 'Change Printer "'+curprinter.printername+'"'
                data['submbutton'] = 'Change printer'
                data['deletebutton'] = 'Delete ' +curprinter.printername
            else:
                return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
        elif (request.POST['action']=='delete'): 
            if('targetid' in request.POST):
                try:
                    curprinter=printer.Printer.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
                curprinter.delete()
                return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
            else:
                return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
        else:
            return redirect(reverse('oneclient', kwargs={'clientid': clientid}))
    else:
        form = PrinterForm(initial={'company': b})
        data['action']='add'
        data['PAGE_TITLE'] = 'New Printer: CMS infotek'
        data['minititle'] = 'Add printer'
        data['submbutton'] = 'Add printer'
    data['form'] = form
    data['built'] = datetime.now().strftime("%H:%M:%S") 
    data['backurl'] = reverse('oneclient', kwargs={'clientid': clientid})
    return render(request, 'forms/unimodelform.html', data, content_type='text/html')
