#pokedex/admin.py

from django.contrib.admin.filters import AllValuesFieldListFilter
from django.contrib import admin
from image_cropping import ImageCroppingMixin

from .models import Sample

class SampleAdmin(ImageCroppingMixin, admin.ModelAdmin):
	# filter_vertical = ('associated_project',)
	# list_filter = ('associated_project',)
        list_filter = ('edge',)
        
        
class ProjectAdmin(admin.ModelAdmin):
	list_filter = ('is_archived',)

class User_ProjectAdmin(admin.ModelAdmin):
	filter_vertical = ('active_project',)

admin.site.register(Sample, SampleAdmin)
# admin.site.register(Project, ProjectAdmin)
# admin.site.register(User_Project, User_ProjectAdmin)
