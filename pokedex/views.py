#pokedex/views.py
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, CreateView, UpdateView
from django.http import HttpResponseRedirect, Http404, HttpRequest
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import render, render_to_response
from django.forms import ModelForm
from django.db.models import Q
from collections import namedtuple
from django.contrib.auth.models import User
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.conf import settings
#from django.contrib.auth.decorators import user_passes_test
from braces.views import UserPassesTestMixin
import plotly.offline as opy
import plotly.graph_objs as go
import numpy as np, pandas as pd
# from .XAS import load_file_to_dataframe as xas.load_file_to_dataframe

from .models import Sample# , Project, User_Project
from .forms import SampleForm#, SamplePhotoForm
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__)))
import external.XAS as xas
#User Project Authentication

#REDIRECT_UNAUTHORIZED_USER = '/unauthorized/'

#Breadcrumbs
    
breadcrumb = namedtuple('breadcrumb', ('name', 'url'))

class BreadcrumbsMixin():
    """Provides context information to allow the template to render a
    breadcrumb navigation trail.
    """
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        try:
            trail = self.breadcrumbs()
        except AttributeError as e:
            trail = []
            raise
        new_trail = []
        for step in trail:
            try:
                new_trail.append(breadcrumb(*step))
                # Reverse the urls if possible
            except TypeError:
                url = reverse(step)
                name = step.replace('_', ' ').title()
                new_trail.append(breadcrumb(name, url))
        context['breadcrumbs'] = new_trail
        return context

    def breadcrumbs(self):
        msg = "Please override the 'breadcrumbs()' method of {}"
        raise NotImplementedError(msg.format(self.__class__))

# Breadcrumbs definitions
def inventory_breadcrumb():
    return breadcrumb('Home', reverse_lazy('home'))

def pokedex_breadcrumb():
    return [
        inventory_breadcrumb(),
        breadcrumb(
            'Pokedex', reverse_lazy('pokedex')
            )
        ]

        
def sample_breadcrumbs(sample):
    return [
    #    pokedex_breadcrumb(),
        breadcrumb(
            sample.name,
            reverse('sample_detail', kwargs={'id': sample.id})
        )
    ]

# def project_breadcrumbs(project):
#       breadcrumbs = [
#               #inventory_breadcrumb(),
#               breadcrumb(
#                       project.name,
#                       reverse('samples_by_projects', kwargs={'id': project.id})
#               )
#       ]
#       return breadcrumbs

def user_breadcrumb(user):
    breadcrumbs = [
        breadcrumb(
            user.first_name,
            reverse_lazy('user_detail')
        )
    ]
    return breadcrumbs

class Main(ListView):
    template_name = 'pokedex/sample_list.html'
    model = Sample
    context_object_name = 'project'

    def breadcrumbs(self):
        breadcrumbs = [inventory_breadcrumb()]
        return breadcrumbs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        samples = Sample.objects.all()
        searchstring = self.request.GET.get('search')
        if searchstring:
             samples = samples.filter(Q(sample_number__icontains=searchstring) | Q(name__icontains=searchstring) | Q(stripped_formula__icontains=searchstring))
        context['samples'] = samples
        context['active_search'] = self.request.GET.get('search')
        return context

class SampleListView(BreadcrumbsMixin, UserPassesTestMixin, DetailView):
    """View that shows all Samples currently under the specified Project"""
    
    template_name = 'pokedex/sample_list.html'
    # model = Project
    context_object_name = 'project'
    login_url = '/unauthorized/'
    redirect_field_name = ''
        
    def breadcrumbs(self):
        return project_breadcrumbs(self.object)

    def test_func(self, user, *args, **kwargs):
        project = self.get_object()
        user_project = User_Project.objects.all().filter(active_project = project, user_id = user)
        if user_project or user.is_superuser:
            return True
        else:
            return False
    
    def get_context_data(self, *args, **kwargs):
        #sample = self.get_object()
        project = self.get_object()
        context = super().get_context_data(*args, **kwargs)
        samples = Sample.objects.all().filter(associated_project = project)
        searchstring = self.request.GET.get('search')
        if searchstring:
             samples = samples.filter(Q(sample_number__icontains=searchstring) | Q(name__icontains=searchstring) | Q(stripped_formula__icontains=searchstring))
        context['samples'] = samples
        context['active_search'] = self.request.GET.get('search')
        return context

    def get_object(self):
        """Return the specific Project by its primary key ('pk')."""
            # Find the primary key from the url
        pk = self.kwargs['id']
            # Get the actual Project object
        project = Project.objects.get(pk=pk)
        return project

class AddSampleView(BreadcrumbsMixin, CreateView):
    template_name = 'pokedex/sample_add.html'
    #success_url = reverse_lazy('home')
    form_class = SampleForm

    def breadcrumbs(self):
        breadcrumbs = [
        #inventory_breadcrumb(),
        breadcrumb('Add Sample',reverse_lazy('add_sample'))
    ]
        return breadcrumbs
    
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        # if obj.XAS_file:
        #     obj.XAS_file
        #self.object = obj.save()
        return HttpResponseRedirect(obj.get_absolute_url())       

    def get_context_data(self, *args, **kwargs):
        context = super(AddSampleView, self).get_context_data(*args, **kwargs)
        context.update(sample_form=SampleForm())
        return context

    def get_form_kwargs(self):
        kwargs = super(AddSampleView, self).get_form_kwargs()
        kwargs.update({"request": self.request.user})
        return kwargs

class EditSampleView(BreadcrumbsMixin, UpdateView):
    template_name = 'pokedex/sample_edit.html'
    template_object_name = 'sample'
    model = Sample
    form_class = SampleForm
    
    def get_object(self):
        """Returns the specific sample by its id"""
        id = self.kwargs['id']
        sample = Sample.objects.get(id=id)
        return sample

    def form_valid(self,form):
        obj = form.save(commit=False)
        obj.save()
        form.save_m2m()
        return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super(EditSampleView, self).get_form_kwargs()
        kwargs.update({"request": self.request.user})
        return kwargs
    
    def breadcrumbs(self):
        breadcrumbs = [
            #inventory_breadcrumb(),
            #sample_breadcrumbs(self.object),
            breadcrumb(
                'Edit Sample',
                reverse(
                    'edit_sample',
                    kwargs={'id': self.object.id})
            )
        ]
        return sample_breadcrumbs(self.object) + breadcrumbs

# class EditSamplePhotoView(BreadcrumbsMixin, UpdateView):
#       template_name = 'pokedex/sample_photo_edit.html'
#       template_object_name = 'sample'
#       model = Sample
#       form_class = SamplePhotoForm
        
#       def breadcrumbs(self):
#               breadcrumbs = [
#                       #inventory_breadcrumb(),
#                       #sample_breadcrumbs(self.object),
#                       breadcrumb(
#                               'Edit Photo',
#                               reverse(
#                                       'edit_sample_photo',
#                                       kwargs={'id': self.object.id})
#                       )
#               ]
#               return sample_breadcrumbs(self.object) + breadcrumbs
        
#       def get_object(self):
#               """Returns the specific sample by its id"""
#               id = self.kwargs['id']
#               sample = Sample.objects.get(id=id)
#               return sample

#       def form_valid(self,form):
#               obj = form.save(commit=False)
#               obj.save()
#               return HttpResponseRedirect(self.get_success_url())
        
    
class SampleDetailView(BreadcrumbsMixin, DetailView):
    template_name = 'pokedex/sample_detail.html'
    template_object_name = 'sample'
    
    def breadcrumbs(self):
        return sample_breadcrumbs(self.object)

    def get_object(self):
        """Return the specific sample by its id"""
        id = self.kwargs['id']
        sample = Sample.objects.get(id=id)
        return sample

    def get_context_data(self, *args, **kwargs):
        sample = self.get_object()
        context = super().get_context_data(*args, **kwargs)

        if sample.file_XAS:
            print ('[DEBUG]', sample.file_XAS.name, type(sample.file_XAS.name))
            # df = self.make_XAS_data(filename=sample.file_XAS.name, beamline=sample.beamline)
            df = xas.load_file_to_dataframe(filename=settings.MEDIA_ROOT + sample.file_XAS.name, beamline=sample.beamline)
            if type(df) == pd.core.frame.DataFrame:
                norm_tey = self.normalize_dataframe(df['TEY'])
                norm_tfy = self.normalize_dataframe(df['TFY'])
                
                # Borrowed from http://stackoverflow.com/questions/36846395/embedding-a-plotly-chart-in-a-django-template
                trace1 = go.Scatter(
                    x=df.index.values,
                    y=norm_tey.values,
                    marker={'color': 'red', 'symbol': 104, 'size': "10"},
                    mode="lines",  name='TEY')
                
                trace2 = go.Scatter(
                    x=df.index.values,
                    y=norm_tfy.values,
                    marker={'color': 'blue', 'symbol': 104, 'size': "10"},
                    mode="lines",  name='TFY', visible='legendonly')
                
                data=go.Data([trace1, trace2])
                layout=go.Layout(title="Mn L-edge", xaxis={'title':'eV'}, yaxis=dict(showline=False, showticklabels=False))
                figure=go.Figure(data=data,layout=layout)
                div = opy.plot(figure, auto_open=False, output_type='div')
                
                context['graph'] = div
        return context

    
    # def make_XAS_data(filename, beamline):
    #     """Calculates XAS data from an input file"""
    #     return xas.load_file_to_dataframe(filename=settings.MEDIA_ROOT + filename, beamline=beamline)
    #     # '/home/mike/Projects/professor_oak/media_files/pokedex/data/XAS/JWFJune15_2.0013'

    def normalize_dataframe(self, dataframe):
        """Normalizes values between 0 and 1"""
        max_val = dataframe.max()
        min_val = dataframe.min()
        normalized_dataframe = (dataframe - min_val) / (max_val - min_val)
        return normalized_dataframe

        
class UserView(BreadcrumbsMixin, DetailView):
    model = User
    template_name = 'pokedex/user_detail.html'
    context_object_name = 'target_user'
    
    def breadcrumbs(self):
        return user_breadcrumb(self.object)
    
    def get_object(self):
        user = self.request.user
        return user
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # project = Project.objects.all()
        user = self.get_object
        # user_project = User_Project.objects.all().filter(user = user)
        #find project objects
        # projects = Project.objects.all().filter(user_project = user_project)
        # context['projects'] = projects
        context['samples'] = Sample.objects.all()
        return context

def unauthorized(request):
    """A user has tried to authorize but failed, maybe not in the database."""
    context = {}
    return render(request, 'pokedex/unauthorized.html', context)
