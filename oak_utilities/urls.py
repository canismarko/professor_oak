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
	url(r'^make_ulon/send_ulon_email/(?P<ulon>[0-9]+)/$',
		login_required(views.send_ulon_email),
		name='send_ulon_email'),
	url(r'^stock_take/$',
		login_required(views.UploadInventoryView.as_view()),
		name='stock_take'),
	url(r'^stock_take/(?P<pk>[0-9]+)/$',
		login_required(views.InventoryResultsView.as_view()),
		name='stock_take_result'),
	url(r'^stock_take/(?P<pk>[0-9]+)/email_results/$',
		views.send_stock_email,
		name='send_stock_email')
	
]

# URLs for the browsable API
router = routers.DefaultRouter()
router.register(r'stock_take', views.StockViewSet, base_name="stock_take")

# Add API URLs to Django's urls
urlpatterns += [
    url(r'^api/', include(router.urls, namespace="util_api")),
]
