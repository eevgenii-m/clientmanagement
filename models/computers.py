from django.db import models
from datetime import datetime
from models import networkequipment
from django.core.validators import MaxValueValidator, MinValueValidator
from models import person
from models import client

class Computer(networkequipment.NetworkEquipment):
    OPERATING_SYSTEMS = (
        ('W10', 'Windows 10'),
        ('W8', 'Windows 8'),
        ('W7', 'Windows 7'),
        ('WS19', 'Windows Server 2019'),
        ('WS16', 'Windows Server 2016'),
        ('WS12', 'Windows Server 2012'),
        ('WS08', 'Windows Server 2008'),
        ('WS03', 'Windows Server 2003'),
        ('MJ', 'MacOS Majovang'),
        ('MHS', 'MacOS High Siera'),
        ('MS', 'MacOS Siera'),
        ('WXP', 'Windows XP'),
        ('WO', 'Windows Other'),
        ('MO', 'MacOS Other'),
        ('O', 'Other'),
    )
    MANUFACTURER = (
        ('D', 'DELL'),
        ('H', 'HP'),
        ('L', 'Lenovo'),
        ('M', 'Microsoft'),
        ('G', 'Apple'),
        ('A', 'Asus'),
        ('S', 'Sony'),
        ('C', 'Acer'),
        ('O', 'Other')
    )
    computername = models.CharField('Computer Name', max_length=40, null=False)
    operatingsystem = models.CharField(max_length=4, null=False, default='W10', blank=False, choices=OPERATING_SYSTEMS)
    manufacturer = models.CharField(max_length=1, null=False, default='D', blank=False, choices=MANUFACTURER)
    model = models.CharField(max_length=60, null=True, default='', blank=True)
    compmonth = models.IntegerField("Recieved Month (enter a number)", blank=True, null=True, default=None, validators=[MaxValueValidator(12), MinValueValidator(1)])
    compyear = models.IntegerField("Recieved Year (enter a number)", blank=True, null=True, default=None, validators=[MaxValueValidator(2030), MinValueValidator(2000)])
    serialnumber = models.CharField(max_length=60, null=True, default='', blank=True)
    user = models.ManyToManyField(person.Person, blank=True, related_name='computer')
    
    def __str__(self):
        return self.computername
