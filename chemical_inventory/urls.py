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
        views.breadcrumbs([views.main_breadcrumb(), 'chemical_list'])(views.ChemicalListView.as_view()),
        name='chemical_list'),
    url(r'^chemicals/(?P<pk>[0-9]+)/$',
        views.ChemicalDetailView.as_view(),
        name='chemical_detail'),
    url(r'^chemicals/edit/(?P<pk>[0-9]+)/$',
	login_required(views.EditChemicalView.as_view()),
	name='chemical_edit'),
    url(r'^containers/add/$',
        login_required(views.AddContainerView.as_view()),
        name='add_container'),
    url(r'^containers/edit/(?P<pk>[0-9]+)/$',
	login_required(views.EditContainerView.as_view()),
	name='container_edit'),
    url(r'^containers/(?P<container_pk>[0-9]+)/supportingdocuments/$',
        views.SupportingDocumentView.as_view(),
        name='supporting_documents'),
    url(r'^containers/(?P<container_pk>[0-9]+)/label/$',
        views.print_label,
        name='print_label'),
    url(r'^containers/(?P<container_pk>[0-9]+)/empty/$',
        views.get_quick_empty,
        name='quick_empty'),
]

# URLs for the browsable API
router = routers.DefaultRouter()
router.register(r'chemicals', views.ChemicalViewSet, base_name="chemical")
router.register(r'containers', views.ContainerViewSet, base_name="container")
router.register(r'gloves', views.GloveViewSet, base_name="glove")
router.register(r'suppliers', views.SupplierViewSet, base_name="supplier")

# Add API URLs to Django's urls
urlpatterns += [
    url(r'^api/', include(router.urls, namespace="api")),
]
