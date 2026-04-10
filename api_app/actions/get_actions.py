from models import computers
from models import client
from models import domain
from api_app.model_files import apikeysmodel


def get_client(clientuuid):
    try:
        cur_client = client.Client.objects.get(unid=clientuuid)
    except Exception as err:
        return None
    return cur_client


def get_computer_by_ser_number(serial_number):
    try:
        cur_comp = computers.Computer.objects.filter(serialnumber=serial_number)
    except Exception as err:
        return None
    if cur_comp is None or len(cur_comp) == 0:
        return None
    return cur_comp[0]

def get_latest_api_key():
    try:
        cur_key = apikeysmodel.APIKey.objects.all().order_by('-expireon', '-id')
        if len(cur_key) > 0 and not cur_key[0].expired():
            return cur_key[0]
    except Exception as err:
        pass
    return apikeysmodel.APIKey.create_api_key()

def get_user_api_key(user):
    if user is None:
        return None
    try:
        cur_key = apikeysmodel.UserAPIKey.objects.all().filter(key_user=user).order_by('-expireon', '-id')
        if len(cur_key) > 0 and not cur_key[0].expired():
            return cur_key[0]
    except Exception as err:
        pass
    return apikeysmodel.UserAPIKey.create_api_key(user)

def get_all_clients_unid_name():
    try:
        clients = client.Client.objects.all().order_by('name')
        result = []
        for cl in clients:
            result.append({'unid': cl.unid, 'name': cl.name})
        return result
    except Exception as err:
        pass
    return None

def get_name(dict):
    return dict['name']

def get_domain_clients_unid_name():
    try:
        domains = domain.Domain.objects.all()
        result = []
        for dom in domains:
            result.append({'unid': dom.company.unid, 'name': dom.company.name})
        result.sort(key=get_name)
        return result
    except Exception as err:
        pass
    return None

def get_domain_info_for_client(curcl):
    try:
        dom = domain.getDomain(curcl)
        result = {'domain': dom.domainnameshort, 'domain_long': dom.domainnamelong, 'admin': dom.admin, 'dns': dom.dnsip}
        return result
    except:
        pass
    return None
