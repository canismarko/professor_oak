from django.shortcuts import render
from collections import namedtuple
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse
from .forms import ULONtemplateForm
from pylatex import Document, Section, Subsection, Tabular, Math, TikZ, Axis, \
	Plot, Figure, Package
from pylatex.utils import italic, escape_latex
import os, subprocess
from datetime import datetime, timedelta, date, time
from professor_oak.views import breadcrumb, BreadcrumbsMixin

# Breadcrumbs definitions
def utilities_breadcrumb():
    return breadcrumb('Utilities', reverse_lazy('utilities_main'))

class Main(BreadcrumbsMixin, TemplateView):
    template_name = 'utilities_main.html'

    # def get_context_data(self, *args, **kwargs):
        # context = super().get_context_data(*args, **kwargs)
        # return context

    def breadcrumbs(self):
        breadcrumbs = [utilities_breadcrumb()]
        return breadcrumbs

    
class GenerateULONView(BreadcrumbsMixin, FormView):
    template_name = 'make_ulon.html'
    form_class = ULONtemplateForm
    
    def breadcrumbs(self):
        breadcrumbs = [
        utilities_breadcrumb(),
        'make_ulon'
        ]
        return breadcrumbs
  
    def form_valid(self, form):
        '''Use the items in ULON form to generate the ULON using LaTeX'''
        filename = './oak_utilities/ULONs/' + "ULON - " + str(date.today()) + ' - ' + datetime.now().time().strftime("%H-%M-%S")
        doc = Document(default_filepath=filename)
        
        #Set Experimental Parameters
        ExperimentStart = form.cleaned_data['experiment_start']
        ExperimentStartTime = form.cleaned_data['experiment_start_time']
        ExperimentEnd = form.cleaned_data['experiment_end']
        ExperimentEndTime = form.cleaned_data['experiment_end_time']
        User = self.request.user.get_full_name()
        ContactNumber = form.cleaned_data['contact_number']
        Chemicals = form.cleaned_data['chemicals']
        ExperimentDescription = form.cleaned_data['experiment_description']
        ExperimentLocation = form.cleaned_data['experiment_location']
        ExperimentSublocation = form.cleaned_data['experiment_sublocation']
        EmergencyShutdown = form.cleaned_data['emergency_shutdown_procedure']
        list_of_hazards = form.list_of_hazards
        Hazards = form.cleaned_data['hazards']
        AdditionalHazards = form.cleaned_data['additional_hazards']
        
        #Reassign commands with \newcommand
        doc.preamble.append(r'\usepackage{import}')
        doc.preamble.append(r'\newcommand{\ExperimentStart}{' + str(ExperimentStart) + '}')
        if ExperimentStartTime is not None:
            doc.preamble.append(r'\newcommand{\ExperimentStartTime}{' + str(ExperimentStartTime)[:-3] + '}')
        doc.preamble.append(r'\newcommand{\ExperimentEnd}{' + str(ExperimentEnd) + '}')
        if ExperimentEndTime is not None:
            doc.preamble.append(r'\newcommand{\ExperimentEndTime}{' + str(ExperimentEndTime)[:-3] + '}')
        doc.preamble.append(r'\newcommand{\User}{' + User + '}')
        doc.preamble.append(r'\newcommand{\ContactNumber}{' + ContactNumber + '}')
        doc.preamble.append(r'\newcommand{\Chemicals}{' + Chemicals + '}')
        doc.preamble.append(r'\newcommand{\ExperimentDescription}{' + ExperimentDescription + '}')
        doc.preamble.append(r'\newcommand{\ExperimentLocation}{' + ExperimentLocation + '}')
        if ExperimentSublocation is not None: #for not required fields
            doc.preamble.append(r'\newcommand{\ExperimentSublocation}{' + ExperimentSublocation + '}')
        doc.preamble.append(r'\newcommand{\EmergencyShutdown}{' + EmergencyShutdown + '}')
        if AdditionalHazards is not None: #for not required fields
            doc.preamble.append(r'\newcommand{\AdditionalHazards}{' + AdditionalHazards + '}')
        for (command, hazard) in list_of_hazards:
            if command in Hazards:
                doc.preamble.append('\\newcommand{\\' + command + ' }{ ' + hazard + '}')
        doc.preamble.append(r'\subimport{../static/}{ULONtemplate.tex}')
        
        #Generate the pdf
        # doc.generate_tex()
        doc.generate_pdf()
        with open(filename + '.pdf', 'rb') as pdf:
            response = HttpResponse(pdf.read(),content_type='application/pdf')
            response['Content-Disposition'] = 'filename=' + filename + '.pdf'
            return response
        pdf.closed