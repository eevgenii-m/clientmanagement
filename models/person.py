from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from models import client
from phonenumber_field.modelfields import PhoneNumberField

class Person(models.Model):
    firstname = models.CharField('First Name', max_length=60)
    lastname = models.CharField('Last Name', max_length=60)
    email = models.EmailField('Email', max_length=254, null=True, blank=True)
    phone = PhoneNumberField('Phone Number', help_text= "In the following format: +10000000000x0000, if you need extension", null=True, default=None, blank=True)
    annoyance = models.fields.PositiveSmallIntegerField('Annoyance level', null=False, default='0', validators=[MaxValueValidator(10), MinValueValidator(0)])
    employedby = models.ForeignKey(client.Client, verbose_name='Employed by', null=True, default='', blank=True, related_name='employees', on_delete=models.CASCADE)
    description = models.TextField('Additional information', null=True, default='', blank=True)

    def create(first='', last='', email='', phone=None, annoyance=0, description='', company=[]):
        person = Person(firstname=first, lastname=last, email=email, phone=phone, annoyance=annoyance)
        return Person()
    
    def name(self):
        return self.firstname + ' ' +self.lastname
    
    def __str__(self):
        return self.name()
