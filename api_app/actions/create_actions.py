from models import computers
from api_app.actions import get_actions
from django.core import validators
from netaddr import EUI


def parse_connection_type(contype):
    return contype

def parse_ip_type(iptype):
    return iptype

def parse_operating_system(opsystem):
    return opsystem

def parse_manufacturer(manuf):
    return manuf


def validate_field(function, value):
    try:
        result = function(value)
        return True
    except Exception as exc:
        return False


def update_computer_with_ser_number(sernumb, name, opsystem, manuf=None, model=None, contype=None, iptype=None, ipaddress=None, macaddress=None, company=None, year=None, month=None):
    comp = get_actions.get_computer_by_ser_number(sernumb)
    if comp is None:
        try:
            return True, create_computer(sernumb=sernumb, name=name, opsystem=opsystem, manuf=manuf, model=model, contype=contype, 
                            iptype=iptype, ipaddress=ipaddress, macaddress=macaddress, company=company, year=year, month=month)
        except Exception:
            return False, None
    comp.computername = name
    comp.operatingsystem = parse_operating_system(opsystem)
    comp.serialnumber = sernumb
    if manuf is not None:
        comp.manufacturer = parse_manufacturer(manuf)
    if model is not None:
        comp.model = model
    if contype is not None:
        comp.connection_type = parse_connection_type(contype)
    if iptype is not None:
        comp.ip_type = parse_ip_type(iptype)
    if ipaddress is not None and validate_field(validators.validate_ipv46_address, ipaddress):
        comp.ip_address = ipaddress
    if macaddress is not None and validate_field(EUI, macaddress):
        comp.mac_address = macaddress
    if company is not None:
        comp.company = company
    if year is not None:
        comp.compyear = year
    if month is not None:
        comp.compmonth = month
    try:
        comp.save()
    except Exception:
        return False, comp    
    return True, comp


def create_computer(sernumb=None, name=None, opsystem=None, manuf=None, model=None, contype=None, iptype=None, ipaddress=None, macaddress=None, company=None, year=None, month=None):
    try:
        comp = computers.Computer(computername=name)
        comp.operatingsystem = parse_operating_system(opsystem)
        comp.serialnumber = sernumb
        if company is not None:
            comp.company = company
        else:
            return None
        if manuf is not None:
            comp.manufacturer = parse_manufacturer(manuf)
        if model is not None:
            comp.model = model
        if contype is not None:
            comp.connection_type = parse_connection_type(contype)
        if iptype is not None:
            comp.ip_type = parse_ip_type(iptype)
        if ipaddress is not None and validate_field(validators.validate_ipv46_address, ipaddress):
            comp.ip_address = ipaddress
        if macaddress is not None and validate_field(EUI, macaddress):
            comp.mac_address = macaddress
        if year is not None:
            comp.compyear = year
        if month is not None:
            comp.compmonth = month
        comp.save()
        return comp
    except Exception as exc:
        print(exc)
        return None
