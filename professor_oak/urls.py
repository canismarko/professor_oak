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
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import admin
from django.views import static
from django.views.generic.base import RedirectView
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf import settings
from django.conf.urls import include, url  # For django versions before 2.0
# from django.urls import include, path  # For django versions from 2.0 and up
from djng.views.upload import FileUploadView


from . import views
import chemical_inventory.urls
import oak_utilities.urls

urlpatterns = [
        # Since there's home content yet, temporarily redirect to the chemical inventory
        url(r'^$', RedirectView.as_view(url='/chemical_inventory/', permanent=False),
            name='home'),
        url(r'^admin/', admin.site.urls),
        url(r'^chemical_inventory/', include(chemical_inventory.urls)),
        url(r'^utilities/', include(oak_utilities.urls)),
        url(r'^users/(?P<pk>\d+)/$',
            login_required(views.UserView.as_view()),
            name="user_detail"),
        url(r'^upload/$', FileUploadView.as_view(), name='fileupload'),
        # Authorization stuff using Django backend
        url(r'^accounts/login/',
            TemplateView.as_view(template_name='login.html'), name='login_page'),
        url(r'^accounts/logout/', logout,
            {'next_page': '/'}, name="logout"),
        # Authorization stuff using python-social-auth
        # url('', include('social_django.urls', namespace='social')),
        # url('', include('social.apps.django_app.urls', namespace='social')),
        # Jasmine unit-test runner
        url(r'^jasmine/$', TemplateView.as_view(template_name='jasmine.html')),
]

# User uploaded content
if settings.DEBUG:
        import debug_toolbar
        urlpatterns.extend([
                # static files (images, css, javascript, etc.)
                url(r'^media/(?P<path>.*)$', static.serve,
                    { 'document_root': settings.MEDIA_ROOT }
                ),
                # For including the Django Debug Toolbar
                url(r'^__debug__/', include(debug_toolbar.urls)),
        ])
