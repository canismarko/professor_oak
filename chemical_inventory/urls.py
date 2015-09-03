"""Define url routing for the chemical inventory application."""

from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^$', views.main, name='inventory_main'),
]
