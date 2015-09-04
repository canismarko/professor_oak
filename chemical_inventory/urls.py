"""Define url routing for the chemical inventory application."""

from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^$', views.main, name='inventory_main'),
    url(r'^chemicals/$', views.ChemicalListView.as_view(), name='chemical_list'),
    url(r'^chemicals/(?P<pk>[0-9]+)/$', views.ChemicalDetailView.as_view(), name='chemical_detail'),
    url(r'^containers/add/$', views.AddContainerView.as_view(), name='add_container'),
]
