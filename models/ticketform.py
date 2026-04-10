from django import forms
from django.conf import settings
import collections, copy
from clientmanagement import modelgetters, sendemail, error_views
from clientmanagement import views as main_views
from clientmanagement.widget import quill
from django.urls import reverse
from django.shortcuts import render, redirect
from datetime import datetime
from phonenumber_field.formfields import PhoneNumberField
from models import ticket, ticket_commentform, uploaded_file
from django.contrib.sites.shortcuts import get_current_site
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Invisible


class TicketForm(forms.ModelForm):
    description = quill.QuillField(label="Problem description")
    contactphone = PhoneNumberField(label="Contact phone number", required=False, help_text="You can add the extension after an x")
    rcaptcha = ReCaptchaField(label='', required=True, error_messages={'required': 'Please, check the box to prove you are not a robot'}, public_key=settings.RECAPTCHA_CHECKBOX_PUBLIC_KEY, private_key=settings.RECAPTCHA_CHECKBOX_PRIVATE_KEY)
    
    file_field = forms.FileField(label="Attach files", widget=forms.ClearableFileInput(), required=False)
    order = ("title", "companyname", "contactname", "contactemail", "contactphone", "description", "file_field", "rcaptcha")
    class Meta:
        model = ticket.Ticket
        fields = ("title", "companyname", "contactname", "contactemail", "description")


    def __init__(self, *args, **kwargs): 
        super(TicketForm, self).__init__(*args, **kwargs)
        tmp = self.fields
        self.fields = collections.OrderedDict()
        for item in self.order:
            self.fields[item] = tmp[item]
        try:
            if (settings.CANCEL_CAPTCHA):
                self.fields.pop('rcaptcha')
        except Exception:
            pass

        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            if (not instance.contactphone is None) and (instance.contactphone != ""):
                self.fields['contactphone'].initial = instance.contactphone.as_national

    def save(self, commit=True, request=None):
        ticket = super(TicketForm, self).save(commit=False)
        if ('contactphone' in self.changed_data):
            ticket.contactphone= self.cleaned_data["contactphone"]
        if commit:
            ticket.save()
        return ticket

    def get_files(self, request):
        return request.FILES.getlist('file_field')


class TicketFormFull(TicketForm):
    order = ("title", "assignedto", "companyname", "contactname", "contactemail", "contactphone", "description")

    class Meta(TicketForm.Meta):
        fields = ("title", "assignedto", "companyname", "contactname", "contactemail", "description")

    def __init__(self, *args, **kwargs): 
        super(TicketFormFull, self).__init__(*args, **kwargs)

    def save(self, commit=True, request=None):
        ticket = super(TicketFormFull, self).save(commit=False, request=request)
        assignedchanged = False
        if ("assignedto" in self.changed_data):
            assignedchanged = not ticket.assignedto is None
        if commit:
            ticket.save()
        return ticket, assignedchanged


def TicketFormParse(request):    
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    data={}
    data['PAGE_TITLE'] = 'Change posted update: CMS infotek'
    if (request.method == 'POST') and ('action' in request.POST):
        if (request.POST['action']=='add'):
            form = TicketForm(request.POST)
            if form.is_valid():
                model = form.save(commit=False)
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = x_forwarded_for.split(',')[0]
                else:
                    ip = request.META.get('REMOTE_ADDR')
                model.senderipaddress = ip
                model.save()
                files = form.get_files(request)
                for f in files:
                    uploaded_file.save_file_ticket(model, f)
                model.sendemail()
                return redirect(reverse('ticket_submitted'))
            else:
                data['action']='add'
                data['PAGE_TITLE'] = 'Submit a ticket: CMS infotek'
                data['minititle'] = 'Submit a Ticket to Infotek'
                data['submbutton'] = 'Submit'
        else:
            return redirect(reverse('updates'))
    else:
        form = TicketForm()
        data['action']='add'
        data['PAGE_TITLE'] = 'Submit a ticket: CMS infotek'
        data['minititle'] = 'Submit a Ticket to Infotek'
        data['submbutton'] = 'Submit'
    data['form'] = form
    data['built'] = datetime.now().strftime("%H:%M:%S")
    data['needquillinput'] = True
    return render(request, 'forms/unimodelform.html', data, content_type='text/html')


def TicketChangeFormParse(request, ticketid):  
    if not ticketid is None:
        try:
            curticket = ticket.Ticket.objects.get(id=ticketid)
        except Exception:
            return redirect(reverse('alltickets', kwargs={'reqtype': 'o'}))
    else:
        return redirect(reverse('alltickets', kwargs={'reqtype': 'o'}))
    data={}
    data['PAGE_TITLE'] = 'Change ticket update: CMS infotek'
    if (request.method == 'POST') and ('action' in request.POST):
        if (request.POST['action']=='close'):
            curticket.close(request.user)
            return redirect(reverse('alltickets', kwargs={'reqtype': 'o'}))
        elif (request.POST['action']=='open'):
            curticket.open()
            return redirect(reverse('alltickets', kwargs={'reqtype': 'o'}))
        elif (request.POST['action']=='change'):
            form = TicketFormFull(instance=curticket)
            data['action'] = 'changed'
            data['PAGE_TITLE'] = 'Change Ticket: CMS infotek'
            data['minititle'] = 'Change Ticket'
            data['submbutton'] = 'Change ticket'
            data['deletebutton'] = 'Delete ticket'
        elif (request.POST['action']=='changed'):
            form = TicketFormFull(request.POST, instance=curticket)
            if form.is_valid():
                model, needemail = form.save(commit=False)
                model.save()
                if needemail:
                    sendemail.sendemailtouser('emails/ticket_was_assigned_to_you.htm', {'ticket': model,
                    "link": model.generate_link()}, 'New ticket assigned to you', model.assignedto)
                return redirect(reverse('alltickets', kwargs={'reqtype': 'o'}))
            data['action'] = 'changed'
            data['PAGE_TITLE'] = 'Change Ticket: CMS infotek'
            data['minititle'] = 'Change Ticket'
            data['submbutton'] = 'Change ticket'
            data['deletebutton'] = 'Delete ticket'
        elif (request.POST['action']=='delete'):
            curticket.delete()
            return redirect(reverse('alltickets', kwargs={'reqtype': 'o'}))
        else:
            return redirect(reverse('alltickets', kwargs={'reqtype': 'o'}))
    else:
        form = TicketFormFull()
        data['action']='add'
        data['PAGE_TITLE'] = 'Submit a ticket: CMS infotek'
        data['minititle'] = 'Submit a Ticket to Infotek'
        data['submbutton'] = 'Submit'
    data['form'] = form
    data['built'] = datetime.now().strftime("%H:%M:%S") 
    data['needquillinput'] = True
    data['backurl'] = reverse('alltickets', kwargs={'reqtype': 'o'})
    return render(request, 'forms/unimodelform.html', data, content_type='text/html')


def ViewTicketDirectParse(request, ticketuuid):
    data_ticket = modelgetters.form_one_ticket_data(ticketuuid)
    if data_ticket is None:
        return error_views.notfound(request)
    data_comments = ticket_commentform.Ticket_CommentFormCreate(request, ticketuuid)
    data = {**data_comments, **data_ticket}
    data['can_change'] = request.user.is_authenticated
    data['can_comment'] = request.user.is_authenticated
    data['built'] = datetime.now().strftime("%H:%M:%S") 
    data['PAGE_TITLE'] = 'Ticket View: CMS infotek'
    data['needquillinput'] = True
    return render(request, 'views/ticketview.html', data, content_type='text/html')
