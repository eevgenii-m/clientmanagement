from models import client
from models import computers
from models import printer
from models import networkequipment
from models import person
from models import domain
from models import router
from models import updates
from models import ticket
from models import ticket_comment
from models import tools
from models import secretnote
from models import wikiarticle
import uuid


def form_all_clients_data():
    try:
        all_clients = client.Client.objects.all().order_by('name')
    except Exception as err:
        return None
    result = []
    for cl in all_clients:
        person_emails = ' '.join(filter(None, cl.employees.values_list('email', flat=True)))
        result.append({'clientobj': cl, 'clientname': cl.name, 'clientphonenumber': cl.phone, 'person_emails': person_emails})
    return result


def form_all_clients_statistics_data():
    try:
        all_clients = client.Client.objects.all().order_by('name')
    except Exception as err:
        return None
    result = []
    for cl in all_clients:
        result.append(form_client_statistics_data(cl))
    data = {}
    data['clients'] = result
    data['countofclients'] = client.Client.objects.count()
    data['countofcomp'] = computers.Computer.objects.count()
    data['countofpeople'] = person.Person.objects.count()
    data['countofprinters'] = printer.Printer.objects.count()
    data['countofnetworkeq'] = networkequipment.NetworkEquipment.objects.count()
    return data


def form_client_statistics_data(cur_client):
    data = {}
    data['id'] = cur_client.id
    data['name'] = cur_client.name
    data['people'] = cur_client.employees.count()
    data['computers'] = computers.Computer.objects.filter(company=cur_client).count()
    data['printers'] = printer.Printer.objects.filter(company=cur_client).count()
    data['networkeq'] = cur_client.networkequipment.count()
    return data


def form_client_data(clientid):
    try:
        cur_client = client.Client.objects.get(id=clientid)
    except Exception as err:
        return None
    data = {}
    data['client'] = cur_client
    data['clientdescription'] = cur_client.description
    data['clientname'] = cur_client.name
    data['clientid'] = cur_client.id
    data['clientphonenumber'] = cur_client.phone
    if(cur_client.address is None):
        data['clientaddress'] = False
        data['clientaddresslink'] = ""
    else:
        data['clientaddress'] = cur_client.address
        data['clientaddresslink'] = "https://www.google.com/maps/place/"+cur_client.address.replace(" ", "+")
    data['clientnetwork'] = form_client_network_equipment_data(cur_client)
    data['clientcomputers'] = form_client_computers_data(cur_client)
    data['clientprinters'] = form_client_printers_data(cur_client)
    data['clientdomain'] = domain.getDomain(cur_client)
    data['clientrouter'] = router.getRouter(cur_client)
    data['clientpeople'] = form_client_people_data(cur_client)
    return data


def form_client_network_equipment_data(client):
    data=[]
    try:
        neteq = networkequipment.NetworkEquipment.objects.filter(company=client).order_by('ip_address', 'mac_address')
    except Exception as err:
        return []
    return neteq


def form_client_computers_data(client):
    data=[]
    try:
        comps = computers.Computer.objects.filter(company=client)
    except Exception as err:
        return []
    return comps


def form_client_printers_data(client):
    data=[]
    try:
        pr = printer.Printer.objects.filter(company=client)
    except Exception as err:
        return []
    return pr


def form_client_people_data(client): 
    data=[]
    try:
        people = client.employees.all().order_by('firstname', 'lastname')
    except Exception as err:
        return []
    return people


def form_computer_data(computerid):
    data={}
    return data


def form_all_computers_data():
    try:
        comps = computers.Computer.objects.all().order_by('computername')
    
    except Exception as err:
        return None
    return comps


def form_all_people_data():
    try:
        peop = person.Person.objects.all().order_by('firstname', 'lastname')
    
    except Exception as err:
        return None
    return peop


def form_updates_data():
    try:
        posts = updates.SystemUpdates.objects.all().order_by('-postedon')[:10]
    except Exception as err:
        return None
    return {'posts': posts}


def form_all_wiki_data():
    try:
        wiki_art = wikiarticle.WikiArticle.objects.all().order_by('-updatedon')
    except Exception as err:
        return None
    return {'wiki_art': wiki_art}


def form_one_wiki_data(unid):
    try:
        wiki_art = wikiarticle.WikiArticle.objects.get(unid=unid)
    except Exception as err:
        return None
    return {'article': wiki_art}


def form_open_tickets_data():
    try:
        tickets = ticket.Ticket.objects.filter(resolved=False).order_by('-createdon')
    except Exception as err:
        return None
    return {'tickets': tickets}


def form_closed_tickets_data():
    try:
        tickets = ticket.Ticket.objects.filter(resolved=True).order_by('-resolvedon')
    except Exception as err:
        return None
    return {'tickets': tickets}


def form_all_tickets_data():
    try:
        tickets = ticket.Ticket.objects.all().order_by('-createdon')
    except Exception as err:
        return None
    return {'tickets': tickets}


def form_one_ticket_data(ticketuuid):
    try:
        curticket = ticket.Ticket.objects.get(unid=ticketuuid)
    except Exception as err:
        return None
    try:
        curcomments = ticket_comment.TicketComment.objects.filter(initial_ticket=curticket).order_by('createdon')
    except Exception as err:
        curcomments=[]
    return {'ticket': curticket, 'comments': curcomments}

def form_all_notes_data():
    try:
        notes = secretnote.SecretNote.objects.all().order_by('-createdon')
    except Exception as err:
        return None
    return {'allnotes': notes}

def form_one_note_data_external(noteuuid):
    try:
        note = secretnote.SecretNote.objects.get(unid=noteuuid)
    except Exception as err:
        return None
    return {'note': note}

def form_one_note_data_internal(noteid):
    try:
        note = secretnote.SecretNote.objects.get(id=noteid)
    except Exception as err:
        return None
    return {'note': note}

def form_all_tools_data(user):
    try:
        if user.is_authenticated:
            tool = tools.MainTool.objects.all().order_by('-createdon')
        else:
            tool = tools.MainTool.objects.filter(public=1, publicinlist=1).order_by('-createdon')
    except Exception as err:
        return None
    return {'tools': tool}

def form_all_link_tools_data(user):
    try:
        if user.is_authenticated:
            tool = tools.LinkTool.objects.all().order_by('-createdon')
        else:
            tool = tools.LinkTool.objects.filter(public=1, publicinlist=1).order_by('-createdon')
    except Exception as err:
        return None
    return {'tools': tool}

def form_all_file_tools_data(user):
    try:
        if user.is_authenticated:
            tool = tools.FileTool.objects.all().order_by('-createdon')
        else:
            tool = tools.FileTool.objects.filter(public=1, publicinlist=1).order_by('-createdon')
    except Exception as err:
        return None
    return {'tools': tool}
