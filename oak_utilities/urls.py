"""Define url routing for the oak_utilities application."""

from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.conf.urls import include, url
from rest_framework import routers

from . import views

urlpatterns = [
    url(r'^$',
        views.main,
        name='utilities_main'),
    url(r'^make_ulon/$',
        views.breadcrumbs([views.main_breadcrumb(), 'make_ulon']),
        login_required(views.GenerateULONView.as_view()),
        name='make_ulon'),
]