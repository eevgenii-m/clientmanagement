"""
URL patterns for testmodule
"""
from django.urls import path

from clientmanagement.testmodule import views as testmodule_views

urlpatterns = [
    path('', testmodule_views.testmodule, name='testmodule'),
]
