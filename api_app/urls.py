"""visualanalyticsplatform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path, reverse_lazy
from django.contrib.auth import views as auth_views
from django.shortcuts import reverse

from api_app import views as api_views


urlpatterns = [
    path('check/', api_views.check_settings, name='check_settings'),
    path('client/<uuid:clientuuid>/computer', api_views.add_computer_to_client, name='add_computer'),
    path('clients', api_views.get_all_clients, name='get_all_clients'),
    path('domains', api_views.get_domain_clients, name='get_domain_clients'),
    path('domain/<uuid:clientuuid>', api_views.get_domain_info, name='get_domain_info'),
    re_path(r'^.*$', api_views.missed_request, name='missed'),
]
