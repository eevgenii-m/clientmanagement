from django.shortcuts import render
import datetime

def notfound(request, data={}):
    data['PAGE_TITLE'] = 'Not found error: CMS Infotek'
    data['built'] = datetime.datetime.now().strftime("%H:%M:%S")
    data['needdatatables'] = False
    return render(request, 'errors/notfound.html', data, content_type='text/html')
