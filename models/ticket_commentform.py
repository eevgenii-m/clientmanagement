from django import forms
from django.conf import settings
import collections, copy
from clientmanagement import modelgetters, sendemail
from clientmanagement.widget import quill
from clientmanagement import views as main_views
from django.urls import reverse
from django.shortcuts import render, redirect
from datetime import datetime, timezone
from phonenumber_field.formfields import PhoneNumberField
from models import ticket_comment, ticket, uploaded_file
from django.contrib.sites.shortcuts import get_current_site


class Ticket_CommentForm(forms.ModelForm):
    description = quill.QuillField(label='Comment*')
    file_field = forms.FileField(label="Attach files", widget=forms.ClearableFileInput(), required=False)
    

    class Meta:
        model = ticket_comment.TicketComment
        fields = ('description', )

    def save(self, commit=True):
        ticket = super(Ticket_CommentForm, self).save(commit=False)
        return ticket

    def get_files(self, request):
        return request.FILES.getlist('file_field')


def Ticket_CommentFormCreate(request, ticketuuid):
    try:
        curticket = ticket.Ticket.objects.get(unid=ticketuuid)
    except Exception as err:
        return redirect(reverse('alltickets', kwargs={'reqtype': 'o'}))
    data={}
    form = Ticket_CommentForm()
    data['action']='add'
    data['PAGE_TITLE'] = 'Add comment: CMS infotek'
    data['minititle'] = 'Add comment'
    data['submbutton'] = 'Submit'
    data['form'] = form
    data['needquillinput'] = True
    return data


def Ticket_CommentFormParse(request, ticketuuid):
    try:
        curticket = ticket.Ticket.objects.get(unid=ticketuuid)
    except Exception as err:
        return redirect(reverse('alltickets', kwargs={'reqtype': 'o'}))
    data={}
    data['PAGE_TITLE'] = 'Change posted update: CMS infotek'
    if (request.method == 'POST') and ('action' in request.POST):
        if (request.POST['action']=='add'):
            form = Ticket_CommentForm(request.POST)
            if form.is_valid():
                model = form.save(commit=False)
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = x_forwarded_for.split(',')[0]
                else:
                    ip = request.META.get('REMOTE_ADDR')
                model.senderipaddress = ip
                model.initial_ticket = curticket
                if request.user.is_authenticated:
                    model.author_name = request.user.get_full_name()
                    model.author_email = request.user.email
                    model.author = request.user
                else:
                    model.author_name = curticket.author_name
                    model.author_email = curticket.author_email
                    model.author = None
                model.save()
                files = form.get_files(request)
                for f in files:
                    uploaded_file.save_file_comment(model, f)
                if settings.SEND_EMAILS_ON_NEW_TICKET_MANUAL:
                    model.sendemail()
                return redirect(reverse('ticket_view_direct', kwargs={'ticketuuid': ticketuuid}))
            else:
                data['action']='add'
                data['PAGE_TITLE'] = 'Add comment: CMS infotek'
                data['minititle'] = 'Submit'
                data['submbutton'] = 'Submit'
        elif (request.POST['action']=='change'):
            if('targetid' in request.POST):
                try:
                    curcomment=ticket_comment.TicketComment.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('ticket_view_direct', kwargs={'ticketuuid': ticketuuid}))
                if not curcomment.editable():
                    return redirect(reverse('ticket_view_direct', kwargs={'ticketuuid': ticketuuid}))
                else:
                    curcomment.createdon = datetime.now(timezone.utc)
                    curcomment.save()
                form = Ticket_CommentForm(instance=curcomment)
                data['action'] = 'changed'
                data['targetid'] = request.POST['targetid']
                data['PAGE_TITLE'] = 'Change comment: CMS infotek'
                data['minititle'] = 'Change Comment'
                data['submbutton'] = 'Change posted comment'
                data['deletebutton'] = False
            else:
                return redirect(reverse('ticket_view_direct', kwargs={'ticketuuid': ticketuuid}))
        elif (request.POST['action']=='changed'):
            if('targetid' in request.POST):
                try:
                    curcomment=ticket_comment.TicketComment.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('ticket_view_direct', kwargs={'ticketuuid': ticketuuid}))
                if not curcomment.editable():
                    return redirect(reverse('ticket_view_direct', kwargs={'ticketuuid': ticketuuid}))
                form = Ticket_CommentForm(request.POST, instance=curcomment)
                if form.is_valid():
                    model = form.save(commit=False)
                    model.createdon = datetime.now(timezone.utc)
                    model.save()
                    return redirect(reverse('ticket_view_direct', kwargs={'ticketuuid': ticketuuid}))
                curcomment.createdon = datetime.now(timezone.utc)
                curcomment.save()
                data['action'] = 'changed'
                data['targetid'] = request.POST['targetid']
                data['PAGE_TITLE'] = 'Change comment: CMS infotek'
                data['minititle'] = 'Change Comment'
                data['submbutton'] = 'Change posted comment'
                data['deletebutton'] = False
            else:
                return redirect(reverse('ticket_view_direct', kwargs={'ticketuuid': ticketuuid}))
    else:
        form = Ticket_CommentForm()
        data['action']='add'
        data['PAGE_TITLE'] = 'Add comment: CMS infotek'
        data['minititle'] = 'Add comment'
        data['submbutton'] = 'Submit'
    data['form'] = form
    data['built'] = datetime.now().strftime("%H:%M:%S") 
    data['needquillinput'] = True
    data['backurl'] = reverse('ticket_view_direct', kwargs={'ticketuuid': ticketuuid})
    return render(request, 'forms/unimodelform.html', data, content_type='text/html')
