from django.shortcuts import render
from collections import namedtuple
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from .forms import ULONtemplateForm, UploadInventoryForm
from pylatex import Document, Section, Subsection, Tabular, Math, TikZ, Axis, \
	Plot, Figure, Package
from pylatex.utils import italic, escape_latex
import os, subprocess
from django.conf import settings
from datetime import datetime, timedelta, date, time
from professor_oak.views import breadcrumb, BreadcrumbsMixin
from .static import inventory_reader as ir
from .models import stock_take

#import 



# Breadcrumbs definitions
def utilities_breadcrumb():
	return breadcrumb('Utilities', reverse_lazy('utilities_main'))

class Main(BreadcrumbsMixin, TemplateView):
	template_name = 'utilities_main.html'
#	template_name = 'coming_soon.html'		  #Temporary redirect page
	
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

class UploadInventoryView(BreadcrumbsMixin, FormView):
	template_name = 'stock_take.html'
	form_class = UploadInventoryForm
	model = stock_take

	def breadcrumbs(self):
		breadcrumbs = [
		utilities_breadcrumb(),
		'stock_take'
		]
		return breadcrumbs
	
	def get_success_url(self):
		return reverse('stock_take')

	def form_valid(self, form):
		'''Take the uploaded inventory.csv and produce a HTML output comparing the uploaded document with the current database.'''
		file = form.save(commit=True)
#		print('[DEBUG]', file.file, '<-- This is the file name ')
#		print('[DEBUG]', os.path.dirname(os.path.abspath(__file__)))
#		print('[DEBUG]', settings.BASE_DIR)
#		print('[DEBUG]', settings.BASE_DIR + '/' + settings.MEDIA_ROOT + str(file.file)[2:])
		file_upload = settings.BASE_DIR + '/' + settings.MEDIA_ROOT + str(file.file)[2:]
		actual = ir.create_barcode_actual(str(file_upload))
		database = ir.create_barcode_database(str(file_upload))
		accounted_for, not_in_db, not_in_actual = ir.analyse(actual, database)
		print ('Analysis complete...')
		print (str(len(accounted_for)) + ' chemicals accounted for')
		print (str(len(not_in_db)) + ' chemicals found but not active in the database')
		print (not_in_db)
		print (str(len(not_in_actual)) + ' chemicals in the database but not found')
		print (not_in_actual)
		return HttpResponseRedirect(self.get_success_url())
