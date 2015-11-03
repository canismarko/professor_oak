"""Define url routing for the oak_utilities application."""

from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.conf.urls import include, url
from rest_framework import routers

from . import views

urlpatterns = [
    url(r'^make_ulon/$',
        (views.ULONtemplateForm.as_view()),
        name='make_ulon'),
]