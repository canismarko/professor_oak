from django.contrib import admin

from . import models

# Register your models here.
admin.site.register(models.Chemical)
admin.site.register(models.Container)
admin.site.register(models.SupportingDocument)
admin.site.register(models.Glove)
admin.site.register(models.Location)
admin.site.register(models.Supplier)
