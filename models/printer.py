from django.db import models
from datetime import datetime
from models import networkequipment
from django.core.validators import MaxValueValidator, MinValueValidator
from models import person
from models import client

class Printer(networkequipment.NetworkEquipment):
    PRINTER_TYPE = (
        ('BL', 'Black and white, Laser'),
        ('CL', 'Color, Laser'),
        ('BI', 'Black and white, Ink'),
        ('CI', 'Color, Ink'),
        ('L', 'Label'),
        ('O', 'Other'),
    )
    MANUFACTURER = (
        ('H', 'HP'),
        ('S', 'Samsung'),
        ('B', 'Brothers'),
        ('C', 'Canon'),
        ('X', 'Xerox'),
        ('D', 'Dymo'),
        ('O', 'Other')
    )
    printername = models.CharField('Printer Name', max_length=50, null=False)
    manufacturer = models.CharField(max_length=1, null=False, default='H', blank=False, choices=MANUFACTURER)
    printertype = models.CharField(max_length=2, null=False, default='BL', blank=False, choices=PRINTER_TYPE)
    model = models.CharField(max_length=50, null=True, default='', blank=True)
    prmonth = models.IntegerField("Recieved Month (enter a number)", blank=True, null=True, default=datetime.today().month, validators=[MaxValueValidator(12), MinValueValidator(1)])
    pryear = models.IntegerField("Recieved Year (enter a number)", blank=True, null=True, default=datetime.today().year, validators=[MaxValueValidator(2030), MinValueValidator(2000)])
    serialnumber = models.CharField(max_length=40, null=True, default='', blank=True)
    
    def __str__(self):
        return self.printername
