"""Define url routing for the oak_utilities application."""

from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.conf.urls import include, url
from rest_framework import routers

from . import views

urlpatterns = [
    url(r'^$',
        views.Main.as_view(),
        name='utilities_main'),
    url(r'^make_ulon/$',
        login_required(views.GenerateULONView.as_view()),
        name='make_ulon'),
	url(r'^stock_take/$',
		login_required(views.UploadInventoryView.as_view()),
		name='stock_take'),
]
