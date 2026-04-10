"""
Django views for testmodule as an example of Django project structure
"""

from datetime import datetime
from django.shortcuts import render
from django.utils.cache import patch_response_headers
from clientmanagement.views import initRequest

def testmodule(request):
    valid, response = initRequest(request)
    if not valid: return response

    data = {
            'request': request,
            'built': datetime.now().strftime("%H:%M:%S"),
            }

    response = render(request, 'testModule.html', data, content_type='text/html')
    patch_response_headers(response, cache_timeout=request.session['max_age_minutes'] * 60)
    return response
