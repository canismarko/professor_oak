"""Define url routing for the chemical inventory application."""

from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.conf.urls import include, url
from rest_framework import routers

from . import views, reports

urlpatterns = [
    url(r'^$',
        views.Main.as_view(),
        name='inventory_main'),
    url(r'^chemicals/$',
        views.ChemicalListView.as_view(),
        # views.main_breadcrumb(), 'chemical_list'])(views.ChemicalListView.as_view(),
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
    url(r'^containers/(?P<pk>[0-9]+)/$',
        views.container_detail,
	name='container_detail'),    
    url(r'^containers/edit/(?P<pk>[0-9]+)/$',
	login_required(views.EditContainerView.as_view()),
	name='container_edit'),
    url(r'^containers/(?P<container_pk>[0-9]+)/supportingdocuments/$',
        views.SupportingDocumentView.as_view(),
        name='supporting_documents'),
    url(r'^containers/(?P<container_pk>[0-9]+)/label/$',
        views.print_label,
        name='print_label'),
    url(r'^chemicals/by_element/$',
        # views.breadcrumbs([views.main_breadcrumb(), 'chemical_list', 'element_search'])(views.ElementSearchView.as_view()),
        views.ElementSearchView.as_view(),
        name='element_search'),

    # Configurable reports
    url(r'^reports/$', reports.ReportsList.as_view(), name="reports"),
    url(r'^reports/all_chemicals/$', reports.AllChemicals.as_view(), name="all_chemicals"),
    url(r'^reports/active_containers/$',
        reports.ActiveContainers.as_view(),
        name="active_containers"
    ),
    url(r'^reports/expired_containers/$',
        reports.ExpiredContainers.as_view(),
        name="expired_containers"
    ),
    url(r'^reports/containers_by_location/$',
        reports.ContainersByLocation.as_view(),
        name="containers_by_location"
    ),
    url(r'^reports/containers_by_owner/$',
        reports.ContainersByOwner.as_view(),
        name="containers_by_owner"
    ),
    url(r'^reports/all_sops/$',
        reports.StandardOperatingProcedure.as_view(),
        name="sop"
    ),
]

# URLs for the browsable API
router = routers.DefaultRouter()
router.register(r'chemicals', views.ChemicalViewSet, base_name="chemical")
router.register(r'hazards', views.HazardViewSet, base_name="hazard")
router.register(r'containers', views.ContainerViewSet, base_name="container")
router.register(r'gloves', views.GloveViewSet, base_name="glove")
router.register(r'suppliers', views.SupplierViewSet, base_name="supplier")

# Add API URLs to Django's urls
urlpatterns += [
    url(r'^api/', include(router.urls, namespace="api")),
]
