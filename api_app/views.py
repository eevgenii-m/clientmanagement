"""
Core Django views for VAR project
"""
import json, logging, os
from datetime import datetime
from urllib.parse import urlencode, urlparse, parse_qs
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import forms as userforms
from django.urls import reverse
from django.shortcuts import render, redirect
from django.utils.cache import patch_response_headers
from django.conf import settings
from django.middleware import csrf
from django.views.decorators.csrf import csrf_exempt
from api_app.model_files import apikeysmodel
from api_app.actions import get_actions, create_actions
from api_app import request_parser


# Get an instance of a logger
logger = logging.getLogger(__name__)

def generate_default_data(request=None):
    data = {'built': datetime.now().strftime("%H:%M:%S")}
    if request is not None:
        data['csrf'] = csrf.get_token(request) 
    return data


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

    api_secret_key = None
    if request.method == 'POST':
        for p in request.POST:
            pval = request.POST[p]
            pval = pval.replace('+', ' ')
            request.session['requestParams'][p.lower()] = pval
        if 'secret_key' in request.POST:
            api_secret_key = request.POST['secret_key']
    else:
        for p in request.GET:
            pval = request.GET[p]
            pval = pval.replace('+', ' ')

            ## Here check if int or date type params can be placed

            request.session['requestParams'][p.lower()] = pval
        if 'secret_key' in request.GET:
            api_secret_key = request.GET['secret_key']
    
    if not api_secret_key is None:
        valid, api_key = apikeysmodel.APIKey.validate_api(api_secret_key)
        if valid:
            request.api_key = api_key
            return True, None
        else:
            if api_key is None:
                return False, HttpResponse(status=401)
            else:
                return False, HttpResponse(status=401)

    return False, HttpResponse(status=402)


def check_settings(request):
    valid, response = initRequest(request)
    if not valid:
        return response
    data = generate_default_data(request)
    data['success'] = True
    data['expires_on'] = request.api_key.expireon
    return JsonResponse(data, status=200)


@csrf_exempt
def missed_request(request):
    data = {}
    return JsonResponse(data, status=400)


def add_computer_to_client(request, clientuuid):
    valid, response = initRequest(request)
    if not valid:
        return response
    data = generate_default_data(request)
    company = get_actions.get_client(clientuuid)
    if company is not None:
        args = request_parser.computer_update_request(request, company)
        if args is not None:
            success, comp = create_actions.update_computer_with_ser_number(**args)
            if success and comp is not None:
                data['computerid'] = comp.id
                return JsonResponse(data, status=200)
    return JsonResponse(data, status=400)

def get_all_clients(request):
    valid, response = initRequest(request)
    if not valid:
        return response
    data = generate_default_data(request)
    data['client_list'] = get_actions.get_all_clients_unid_name()
    if data['client_list'] is None:
        return JsonResponse(data, status=404)
    return JsonResponse(data, status=200)

def get_domain_clients(request):
    valid, response = initRequest(request)
    if not valid:
        return response
    data = generate_default_data(request)
    data['client_list'] = get_actions.get_domain_clients_unid_name()
    if data['client_list'] is None:
        return JsonResponse(data, status=404)
    return JsonResponse(data, status=200)

def get_domain_info(request, clientuuid):
    valid, response = initRequest(request)
    if not valid:
        return response
    data = generate_default_data(request)
    company = get_actions.get_client(clientuuid)
    if company is not None:
        info = get_actions.get_domain_info_for_client(company)
        if info is not None:
            data['domain'] = info
            return JsonResponse(data, status=200)
    return JsonResponse(data, status=400)
