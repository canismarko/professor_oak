"""Define url routing for the chemical inventory application."""

from django.contrib.auth.decorators import login_required
from django.conf.urls import include, url

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
	url(r'^chemicals/edit/(?P<pk>[0-9]+)/$',
		views.EditChemicalView.as_view(),
		name='chemical_edit'),
    url(r'^containers/add/$',
        login_required(views.AddContainerView.as_view()),
        name='add_container'),
	url(r'^containers/edit/(?P<barcode>[0-9]+)/$',
		views.EditContainerView.as_view(),
		name='container_edit'),
]
