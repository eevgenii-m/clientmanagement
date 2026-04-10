from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from clientmanagement.widget import quill
from django.conf import settings
import os, uuid


class Client(models.Model):
    name = models.CharField('Client Name', max_length=80, null=False)
    address = models.CharField('Client Address', max_length=160, null=True, default='', blank=True)
    phone = PhoneNumberField('Phone Number', help_text= "In the following format: +10000000000x0000, if you need extension", null=True, default=None, blank=True)
    unid = models.UUIDField("Unique ID", default=uuid.uuid4, editable=False, unique=True, blank=False, null=False)
    description = models.TextField('Additional information', null=True, default='', blank=True)

    def get_quill_object(self):
        return quill.QuillObject(self.description)

    def get_file_folder(self):
        folder_path = os.path.join(settings.CLIENT_FILES, str(self.id))
        return folder_path

    def create_add_computer_software(self, api_key):
        sett = {"api_key": api_key.secret_api_key, "clientuuid": str(self.unid), "hostname":settings.EMAIL_HOST_LINK}
        software_file = settings.GET_ADD_COMPUTER_SOFTWARE(sett)
        return open(software_file, "rb")

    def create_add_computer_config(self, api_key):
        sett = {"api_key": api_key.secret_api_key, "clientuuid": str(self.unid), "hostname":settings.EMAIL_HOST_LINK}
        config_info = settings.GET_ADD_COMPUTER_CONFIG_FILE(sett)
        return config_info

    def __str__(self):
        return self.name
