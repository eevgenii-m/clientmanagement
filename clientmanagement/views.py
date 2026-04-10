"""
Core Django views for VAR project
"""
import json, os, logging
from datetime import datetime
from urllib.parse import urlencode, urlparse, parse_qs
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import forms as userforms
from django.urls import reverse
from django.shortcuts import render, redirect
from django.utils.cache import patch_response_headers
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf import settings
from clientmanagement import userfunctions, loginform, modelgetters
from api_app.model_files import apikeysmodel

# Get an instance of a logger
logger = logging.getLogger(__name__)


def initRequest(request):
    """
    A function to check and verify request
    :param request:
    :return:
    """

    url = request.get_full_path()
    u = urlparse(url)
    query = parse_qs(u.query)
    query.pop('timestamp', None)
    try:
        u = u._replace(query=urlencode(query, True))
    except UnicodeEncodeError:
        data = {
            'errormessage': 'Error appeared while encoding URL!'
        }
        return False, HttpResponse(json.dumps(data), content_type='text/html')

    ## Set default page lifetime in the http header, for the use of the front end cache
    request.session['max_age_minutes'] = 10

    ## Create a dict in session for storing request params
    requestParams = {}
    request.session['requestParams'] = requestParams
    if getattr(settings, 'SESSION_COOKIE_AGE', None):
        request.session.set_expiry(settings.SESSION_COOKIE_AGE)

    if request.method == 'POST':
        for p in request.POST:
            pval = request.POST[p]
            pval = pval.replace('+', ' ')
            request.session['requestParams'][p.lower()] = pval
    else:
        for p in request.GET:
            pval = request.GET[p]
            pval = pval.replace('+', ' ')

            ## Here check if int or date type params can be placed

            request.session['requestParams'][p.lower()] = pval

    return True, None

@login_required( login_url = 'login' )
def homepage(request):
    valid, response = initRequest(request)
    if not valid:
        return response
    data = {}
    data['PAGE_TITLE'] = 'CMS Infotek'
    data['built'] = datetime.now().strftime("%H:%M:%S")
    data['needdatatables'] = False
    return render(request, 'index.html', data, content_type='text/html')


@login_required( login_url = 'login' )
def usermanagement(request):
    valid, response = initRequest(request)
    if not valid:
        return response
    data = {}
    if (request.method == 'POST') and ('action' in request.POST):
        if (request.POST['action'] == 'deleteuser') and ('target' in request.POST):
            success, message = userfunctions.deleteUserID(request.POST['target'])
            data['success'] = success
            data['message'] = message
            data['username'] = request.POST['target']
            return JsonResponse(data)
    
    data['userlist'] = userfunctions.getUserList()
    data['PAGE_TITLE'] = 'Manage users: CMS infotek'
    data['built'] = datetime.now().strftime("%H:%M:%S")
    data['needdatatables'] = True
    return render(request, 'user/usermanagement.html', data, content_type='text/html')


@login_required( login_url = 'login' )
def userpersonalpage(request, deleted=0, deletedpage=0):
    valid, response = initRequest(request)
    if not valid:
        return response
    data = {}
    data['deleted'] = deleted != 0
    data['del_page'] = deletedpage != 0
    data['PAGE_TITLE'] = 'Personal page: CMS infotek'
    data['api_key'] = len(apikeysmodel.UserAPIKey.get_api_keys(request.user))>0
    data['built'] = datetime.now().strftime("%H:%M:%S")
    return render(request, 'user/personal/main.html', data, content_type='text/html')


@login_required( login_url = 'login' )
def deletepersonalapikey(request):
    valid, response = initRequest(request)
    if not valid:
        return response
    result = apikeysmodel.UserAPIKey.delete_api_key(request.user)
    return redirect(reverse("personal_page_uri", kwargs={"deleted": 1 if result else 0, "deletedpage":"1"}))


@login_required( login_url = 'login' )
def createuser(request):
    valid, response = initRequest(request)
    if not valid:
        return response
    data = {}

    if (request.method == 'POST') and ('action' in request.POST):
        if (request.POST['action'] == 'validate') and ('target' in request.POST):
            if('value' in request.POST):
                if (request.POST['target']=='username'):
                    success, message = userfunctions.checkUsernameExists(request.POST['value'])
                    return JsonResponse({'success': success, 'message': message})
                elif(request.POST['target']=='email'):
                    success, message = userfunctions.checkEmailExists(request.POST['value'])
                    return JsonResponse({'success': success, 'message': message})
                elif(request.POST['target']=='password'):
                    success, message = userfunctions.checkPasswordComplexity(request.POST['value'])
                    return JsonResponse({'success': success, 'message': message})
                return JsonResponse({'success': False, 'message': 'Could not verify login'})
            else:
                return JsonResponse({'success': False, 'message': 'Could not verify login'})
        if (request.POST['action'] == 'createacc') and ('username' in request.POST) and ('password' in request.POST) and ('email' in request.POST) and \
                    ('firstname' in request.POST) and ('lastname' in request.POST):
            if (userfunctions.validateNewUser(request.POST['username'], request.POST['password'], request.POST['email'], request.POST['firstname'], request.POST['lastname'])):
                try:
                    user = userfunctions.createUser(request.POST['username'], request.POST['password'], request.POST['email'], request.POST['firstname'], request.POST['lastname'])
                    if user is not None:
                        return redirect('/usermanagement')
                except Exception as exc:
                    logger.error('!views.createuser!: Could not create user. \n' + str(exc))
            data['username']=request.POST['username']
            data['password']=request.POST['password']
            data['email']=request.POST['email']
            data['firstname']=request.POST['firstname']
            data['lastname']=request.POST['lastname']
            data['creationfailed']=True
    
    data['PAGE_TITLE'] = 'Create user: CMS Infotek'
    data['built'] = datetime.now().strftime("%H:%M:%S")
    data['needdatatables'] = False
    return render(request, 'user/createuser.html', data, content_type='text/html')


@login_required( login_url = 'login' )
def changeuser(request):
    valid, response = initRequest(request)
    if not valid:
        return response
    data = {}
    if (request.method == 'POST') and ('action' in request.POST):
        if (request.POST['action'] == 'validate') and ('target' in request.POST)and ('curusername' in request.POST):
            if('value' in request.POST):
                if (request.POST['target']=='username'):
                    success, message = userfunctions.checkUsernameExists(request.POST['value'])
                    return JsonResponse({'success': success, 'message': message})
                elif(request.POST['target']=='email'):
                    success, message = userfunctions.checkEmailExists(request.POST['value'], request.POST['curusername'])
                    return JsonResponse({'success': success, 'message': message})
                elif(request.POST['target']=='password'):
                    success, message = userfunctions.checkPasswordComplexity(request.POST['value'])
                    return JsonResponse({'success': success, 'message': message})
                return JsonResponse({'success': False, 'message': 'Could not verify login'})
            else:
                return JsonResponse({'success': False, 'message': 'Could not verify login'})
        elif (request.POST['action'] == 'changeemail') and ('username' in request.POST) and ('password' in request.POST) and ('email' in request.POST) and \
                    ('firstname' in request.POST) and ('lastname' in request.POST):
            if (userfunctions.validateNewUser(request.POST['username'], request.POST['password'], request.POST['email'], request.POST['firstname'], request.POST['lastname'])):
                try:
                    user = userfunctions.createUser(request.POST['username'], request.POST['password'], request.POST['email'], request.POST['firstname'], request.POST['lastname'])
                    if user is not None:
                        return redirect('/usermanagement')
                except Exception as exc:
                    logger.error('!views.createuser!: Could not create user. \n' + str(exc))
        elif (request.POST['action'] == 'changeemail') and ('email' in request.POST):
            try:
                success, message = userfunctions.checkEmailExists(request.POST['email'], request.POST['curusername'])
                if success:
                    if 'id' in request.POST:
                        success = userfunctions.changeEmail( request.POST['email'], request.POST['id'])
                    else:
                        success = userfunctions.changeEmail(request.POST['email'], request.user.id)
                    if user is not None:
                        return redirect('/changeuser')
            except Exception as exc:
                logger.error('!views.createuser!: Could not create user. \n' + str(exc))
        elif (request.POST['action'] == 'change') and ('id' in request.POST):
            cur_user = userfunctions.getUser(request.POST['id'])
            if cur_user is None:
                return redirect(reverse('usermanagement'))
            data['username']=cur_user.username
            data['email']=cur_user.email
            data['firstname']=cur_user.first_name
            data['lastname']=cur_user.last_name   
            data['id']=cur_user.id

    if (request.method == 'GET'):  
        data['username']=request.user.username
        data['email']=request.user.email
        data['firstname']=request.user.first_name
        data['lastname']=request.user.last_name
                
    data['PAGE_TITLE'] = 'change user: CMS Infotek'
    data['built'] = datetime.now().strftime("%H:%M:%S")
    data['needdatatables'] = False
    return render(request, 'user/changeuser.html', data, content_type='text/html')

@login_required( login_url = 'login' )
def clientview(request, clientid):
    valid, response = initRequest(request)
    if not valid:
        return response
    data = modelgetters.form_client_data(clientid)
    if data is None:
        return redirect('/')            
    data['PAGE_TITLE'] = 'Client "'+ data['clientname'] +'": CMS Infotek'
    data['built'] = datetime.now().strftime("%H:%M:%S")
    data['needdatatables'] = False
    data['needquillinput'] = True
    return render(request, 'views/client.html', data, content_type='text/html')


@login_required( login_url = 'login' )
def allclientsview(request):
    valid, response = initRequest(request)
    if not valid:
        return response
    data = {'allclients': modelgetters.form_all_clients_data()}
    if data is None:
        return redirect('/')            
    data['PAGE_TITLE'] = 'All clients: CMS Infotek'
    data['built'] = datetime.now().strftime("%H:%M:%S")
    data['needdatatables'] = True
    return render(request, 'views/allclients.html', data, content_type='text/html')


@login_required( login_url = 'login' )
def allcomputersview(request):
    valid, response = initRequest(request)
    if not valid:
        return response
    data = {'allcomputers': modelgetters.form_all_computers_data()}
    if data is None:
        return redirect('/')            
    data['PAGE_TITLE'] = 'All computers: CMS Infotek'
    data['built'] = datetime.now().strftime("%H:%M:%S")
    data['needdatatables'] = True
    return render(request, 'views/allcomputers.html', data, content_type='text/html')


@login_required( login_url = 'login' )
def allpeopleview(request):
    valid, response = initRequest(request)
    if not valid:
        return response
    data = {'people': modelgetters.form_all_people_data()}
    if data is None:
        return redirect('/')            
    data['PAGE_TITLE'] = 'All people: CMS Infotek'
    data['built'] = datetime.now().strftime("%H:%M:%S")
    data['needdatatables'] = True
    return render(request, 'views/allpeople.html', data, content_type='text/html')


@login_required( login_url = 'login' )
def statisticsview(request):
    valid, response = initRequest(request)
    if not valid:
        return response
    data = modelgetters.form_all_clients_statistics_data()
    if data is None:
        return redirect('/')            
    data['PAGE_TITLE'] = 'Statistics: CMS Infotek'
    data['built'] = datetime.now().strftime("%H:%M:%S")
    data['needdatatables'] = True
    return render(request, 'views/statistics.html', data, content_type='text/html')


@login_required( login_url = 'login' )
def allticketsview(request, reqtype):
    valid, response = initRequest(request)
    if not valid:
        return response
    if not reqtype in ['a', 'c']:
        reqtype='o'
    try:
        if reqtype == 'a':
            data = modelgetters.form_all_tickets_data()
            data['PAGE_TITLE'] = 'All Tickets: CMS Infotek'
            data['subtittle'] = 'All Tickets'
            data['closedticketson'] = True
        elif reqtype == 'c':
            data = modelgetters.form_closed_tickets_data()
            data['PAGE_TITLE'] = 'Closed Tickets: CMS Infotek'
            data['subtittle'] = 'Closed Tickets'
            data['closedticketson'] = True
        else:
            data = modelgetters.form_open_tickets_data()
            data['PAGE_TITLE'] = 'Open Tickets: CMS Infotek'
            data['subtittle'] = 'Open Tickets'
            data['closedticketson'] = False
    except Exception:
        return redirect('/')            
    data['built'] = datetime.now().strftime("%H:%M:%S")
    data['needdatatables'] = True
    data['needquillinput'] = True
    return render(request, 'views/alltickets.html', data, content_type='text/html')


@login_required( login_url = 'login' )
def systemupdatesview(request):
    valid, response = initRequest(request)
    if not valid:
        return response
    data = modelgetters.form_updates_data()         
    data['PAGE_TITLE'] = 'System Updates: CMS Infotek'
    data['built'] = datetime.now().strftime("%H:%M:%S")
    data['needdatatables'] = False
    data['needquillinput'] = True
    return render(request, 'views/updates.html', data, content_type='text/html')


@login_required( login_url = 'login' )
def allWikiArticlesView(request):
    valid, response = initRequest(request)
    if not valid:
        return response
    data = modelgetters.form_all_wiki_data()         
    data['PAGE_TITLE'] = 'Wiki: CMS Infotek'
    data['built'] = datetime.now().strftime("%H:%M:%S")
    data['needdatatables'] = True
    data['needquillinput'] = False
    return render(request, 'views/allwiki.html', data, content_type='text/html')


@login_required( login_url = 'login' )
def wikiArticleView(request, wikiuuid):
    valid, response = initRequest(request)
    if not valid:
        return response
    data = modelgetters.form_one_wiki_data(wikiuuid)         
    data['PAGE_TITLE'] = 'Wiki: CMS Infotek'
    data['built'] = datetime.now().strftime("%H:%M:%S")
    data['needdatatables'] = False
    data['needquillinput'] = True
    return render(request, 'views/wikiview.html', data, content_type='text/html')


#@login_required( login_url = 'login' )
def allToolsView(request, tool_type):
    valid, response = initRequest(request)
    if not valid:
        return response
    if not tool_type in ['l', 'f']:
        tool_type=''
    try:
        if tool_type == 'l':
            data = modelgetters.form_all_link_tools_data(request.user)
            data['PAGE_TITLE'] = 'Link tools: CMS Infotek'
            data['subtittle'] = 'Link tools'
        elif tool_type == 'f':
            data = modelgetters.form_all_file_tools_data(request.user)
            data['PAGE_TITLE'] = 'File tools: CMS Infotek'
            data['subtittle'] = 'File tools'
        else:
            data = modelgetters.form_all_tools_data(request.user)
            data['PAGE_TITLE'] = 'All tools: CMS Infotek'
            data['subtittle'] = 'All tools'
    except Exception as exc:
        print(exc)
    data['built'] = datetime.now().strftime("%H:%M:%S")
    data['needdatatables'] = True
    return render(request, 'views/alltools.html', data, content_type='text/html')


def ticketdoneview(request):
    valid, response = initRequest(request)
    if not valid:
        return response
    data = {}           
    data['PAGE_TITLE'] = 'Ticket submitted: CMS Infotek'
    data['built'] = datetime.now().strftime("%H:%M:%S")
    data['needdatatables'] = False
    return render(request, 'forms/thankyouticket.html', data, content_type='text/html')
