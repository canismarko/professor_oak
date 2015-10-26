"""professor_oak URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse
from django.contrib.auth import views as auth_views
from django.conf import settings

from . import views
import chemical_inventory.urls

urlpatterns = [
        # Since there's home content yet, temporarily redirect to the chemical inventory
        # url(r'^$', views.home, name='home'),
        url(r'^$', RedirectView.as_view(url='/chemical_inventory/', permanent=False),
            name='home'),
        url(r'^admin/', include(admin.site.urls)),
        url(r'^chemical_inventory/', include(chemical_inventory.urls)),

        # Authorization stuff using Persona
        url(r'', include('django_browserid.urls')),
        url(r'^unauthorized/$', views.unauthorized, name='unauthorized'),
        url(r'^accounts/login/$',
            TemplateView.as_view(template_name='login.html'),
            name='login'),
        # Jasmine unit-test runner
        url(r'^jasmine/$', TemplateView.as_view(template_name='jasmine.html')),
]

# User uploaded content
if settings.DEBUG:
        # static files (images, css, javascript, etc.)
        urlpatterns.append(
            url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
                { 'document_root': settings.MEDIA_ROOT }
            ))
