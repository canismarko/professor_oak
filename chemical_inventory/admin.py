from django.contrib import admin

from .models import Chemical, Container, Glove, Location

# Register your models here.
admin.site.register(Chemical)
admin.site.register(Container)
admin.site.register(Glove)
admin.site.register(Location)
