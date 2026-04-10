from django.db import models
from datetime import datetime, timedelta, timezone
import pytz, os, json
from clientmanagement import sendemail
from clientmanagement.widget import quill
from models import ticket
from django.contrib.auth.models import User
from django.conf import settings


class TicketComment(models.Model):
    createdon = models.DateTimeField("Created time", auto_now_add=True, null=False, blank=False)
    author = models.ForeignKey(User, verbose_name="Written by (user)", on_delete=models.SET_NULL, null=True, blank=True)
    author_name = models.CharField("Written by", max_length=120, null=False, blank=False)
    author_email = models.EmailField("Author email", max_length=254)
    description = models.TextField("Comment*", null=False, blank=False)
    senderipaddress = models.GenericIPAddressField("Sender IP address")
    initial_ticket = models.ForeignKey(ticket.Ticket, verbose_name="Ticket subject", on_delete=models.CASCADE, related_name="comments")

    def createtime(self):
        return self.createdon.astimezone(pytz.timezone('America/New_York'))
    
    def __str__(self):
        return "Comment # " + str(self.id)

    def editable(self):
        if datetime.now(timezone.utc) - self.createdon > timedelta(minutes=settings.TIME_TO_EDIT):
            return False
        else:
            return True

    def get_files_folder(self):
        folder_path = os.path.join(self.initial_ticket.get_files_folder(), str(self.id))
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        return folder_path

    def is_quill_content(self):
        return quill.check_quill_string(self.description)

    def get_quill_content(self):
        return quill.get_quill_text(self.description)

    def get_content(self):
        return self.description

    def sendemail(self):
        if True:
            sendemail.sendemailtoone('emails/ticket_update_email.htm', {"ticket": self.initial_ticket, 
            "link": self.initial_ticket.generate_link(), "answerlink": self.initial_ticket.generate_answer_link(),
            "comment": self}, 
            'Update to your ticket', self.initial_ticket.contactemail, self.initial_ticket.contactname)
