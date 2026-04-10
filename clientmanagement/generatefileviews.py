from django.http import HttpResponse, FileResponse
from django.core.files.base import ContentFile
from django.urls import reverse
from django.shortcuts import redirect
from django.conf import settings
from clientmanagement import views as main_views
from models import client
from models import domain
from clientmanagement import modelgetters
from django.contrib.auth.decorators import login_required
from api_app.actions.get_actions import get_latest_api_key, get_user_api_key
from api_app.model_files.apikeysmodel import APIKey
import os


@login_required( login_url = 'login' )
def downloadConnectDomainFile(request, clientid):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    try:
        cur_client = client.Client.objects.get(id=clientid)
    except Exception as err:
        return redirect(reverse('allclients'))
    cur_domain = domain.getDomain(cur_client)
    resfile = cur_domain.DomainLoginFile()
    response = HttpResponse(content_type='text/bat')
    response['Content-Disposition'] = 'attachment; filename="'+resfile['filename']+'"'
    response.write(resfile['file'].getvalue())
    return response
 

@login_required( login_url = 'login' )
def downloadAddComputerSoftware(request, clientid, new_api_key="n"):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    try:
        cur_client = client.Client.objects.get(id=clientid)
    except Exception as err:
        return redirect(reverse('allclients'))
    if new_api_key=="y":
        api_key = APIKey.create_api_key()
    else:
        api_key = get_latest_api_key()
    resfile = cur_client.create_add_computer_software(api_key)
    response = HttpResponse(content_type='application/exe')
    response['Content-Disposition'] = 'attachment; filename="' + os.path.basename(resfile.name) + '"'
    response.write(resfile.read())
    path = resfile.name
    resfile.close()
    try:
        os.remove(path)
    except:
        pass
    return response


@login_required( login_url = 'login' )
def downloadAddComputerConfigFile(request, clientid, new_api_key="y"):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    try:
        cur_client = client.Client.objects.get(id=clientid)
    except Exception as err:
        return redirect(reverse('allclients'))
    if new_api_key=="y":
        api_key = APIKey.create_api_key()
    else:
        api_key = get_latest_api_key()
    resfile = cur_client.create_add_computer_config(api_key)
    response = HttpResponse(content_type='text/xml')
    response['Content-Disposition'] = 'attachment; filename="' + os.path.basename(resfile['name']) + '"'
    for line in resfile['content']:
        response.write(line)
    return response


@login_required( login_url = 'login' )
def downloadUserCMSInteractionSoftware(request):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    
    api_key = get_user_api_key(request.user)
    sett = {"api_key": api_key.secret_api_key, "hostname":settings.EMAIL_HOST_LINK}
    resfile = open(settings.GET_CMS_INTERACTION_SOFTWARE(sett), "rb")
    response = HttpResponse(content_type='application/exe')
    response['Content-Disposition'] = 'attachment; filename="' + os.path.basename(resfile.name) + '"'
    response.write(resfile.read())
    path = resfile.name
    resfile.close()
    try:
        os.remove(path)
    except:
        pass
    return response
