from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, FormView
from .forms import ULONtemplateForm

# Create your views here.
class GenerateULONView(FormView):
    template_name = 'make_ulon.html'
    form_class = ULONtemplateForm