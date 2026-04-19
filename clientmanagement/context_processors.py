from django.conf import settings


def global_settings(request):
    return {
        'VERSION_STATIC_FILES': True if settings.VERSION_STATIC_FILES else False,
        'CLIENTMANAGEMENT_VERSION': settings.CLIENTMANAGEMENT_VERSION,
        'VERSION': settings.CLIENTMANAGEMENT_VERSION,
        'URL_ADD_TO_STATIC_FILES': '?v='+settings.CLIENTMANAGEMENT_VERSION if settings.VERSION_STATIC_FILES else '',
        'needdatatables': False,
        'needquillinput': False,
        'EMAIL_URL_FOR_LINKS': settings.EMAIL_HOST_LINK,
    }
