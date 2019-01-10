from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import TemplateView
from django.conf import settings
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = patterns('',
	#browserid for Persona
	url(r'', include('django_browserid.urls')),
        # Examples:
    	url(r'^$',
		views.Main.as_view(), 
		name='pokedex'),
                       # url(r'^blog/', include('blog.urls')),
	url(r'^accounts/login/$', 
		TemplateView.as_view(template_name='pokedex/login.html'),
		name='login'),
	url(r'^unauthorized/$', 
		TemplateView.as_view(template_name='pokedex/unauthorized.html'),
		name='unauthorized'),
	# url(r'^project/(?P<id>[0-9]+)/$',
	# 	login_required(views.SampleListView.as_view()),
	# 	name='samples_by_projects'),
	url(r'^add/$',
		login_required(views.AddSampleView.as_view()),
		name='add_sample'),
	url(r'^sample/(?P<id>[0-9]+)/$',
		login_required(views.SampleDetailView.as_view()),
		name='sample_detail'),
	url(r'^edit/(?P<id>[0-9]+)/$',
		login_required(views.EditSampleView.as_view()),
		name='edit_sample'),
	# url(r'^edit/(?P<id>[0-9]+)/photo/$',
	# 	login_required(views.EditSamplePhotoView.as_view()),
	# 	name='edit_sample_photo'),	
	url(r'^profile/$',
		login_required(views.UserView.as_view()),
		name='user_detail'),
	url(r'^admin/', include(admin.site.urls)),
	#url(r'^users/(?P<id>\d+)/$',
    #        login_required(views.UserView.as_view()),
    #       name="user_detail"),
)

if settings.DEBUG:
	urlpatterns += patterns('',
		(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
		'document_root': settings.MEDIA_ROOT}))
