from django.db import models
from datetime import datetime
from models import networkequipment
from django.core.validators import MaxValueValidator, MinValueValidator
from models import person
from models import client

class OtherNetworkEquipment(networkequipment.NetworkEquipment):
    equipmenttype = models.CharField('Equipment Type', max_length=50, null=False)
    manufacturer = models.CharField('Manufacturer', max_length=40, null=True, default='', blank=True)
    model = models.CharField('Model', max_length=40, null=True, default='', blank=True)
    serialnumber = models.CharField('Serial number', max_length=50, null=True, default='', blank=True)
    
    def __str__(self):
        return self.equipmenttype
