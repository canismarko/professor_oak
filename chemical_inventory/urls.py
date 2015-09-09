"""Define url routing for the chemical inventory application."""

from django.contrib.auth.decorators import login_required
from django.conf.urls import include, url
from rest_framework import routers

from . import views

urlpatterns = [
    url(r'^$',
        views.main,
        name='inventory_main'),
    url(r'^chemicals/$',
        views.ChemicalListView.as_view(),
        name='chemical_list'),
    url(r'^chemicals/(?P<pk>[0-9]+)/$',
        views.ChemicalDetailView.as_view(),
        name='chemical_detail'),
    url(r'^containers/add/$',
        login_required(views.AddContainerView.as_view()),
        name='add_container'),
]

# URLs for the browsable API
router = routers.DefaultRouter()
router.register(r'chemicals', views.ChemicalViewSet)

# Add API URLs to Django's urls
urlpatterns += [
    url(r'^api/', include(router.urls)),
]
