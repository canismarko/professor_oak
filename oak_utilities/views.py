from django.shortcuts import render
from collections import namedtuple
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from .forms import ULONtemplateForm, UploadInventoryForm
from pylatex import Document, Section, Subsection, Tabular, Math, TikZ, Axis, \
	Plot, Figure, Package
from pylatex.utils import italic, escape_latex
import os, subprocess, csv
from django.conf import settings
from datetime import datetime, timedelta, date, time
from professor_oak.views import breadcrumb, BreadcrumbsMixin
from .static import inventory_reader as ir
from .models import stock_take
from chemical_inventory.models import Container
from rest_framework import viewsets, permissions, response, status
from .serializers import StockSerializer

#email dependencies
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import User
from templated_email import send_templated_mail

# Breadcrumbs definitions
def utilities_breadcrumb():
	return breadcrumb('Utilities', reverse_lazy('utilities_main'))

def stock_breadcrumbs(stock_take):
	return [
		utilities_breadcrumb(),
		'stock_take',
		breadcrumb(
			stock_take.name,
			reverse('results', kwargs={'stock': stock_take.id})
		)
	]

class Main(BreadcrumbsMixin, TemplateView):
	template_name = 'utilities_main.html'
#	template_name = 'coming_soon.html'		  #Temporary redirect page

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

	def breadcrumbs(self):
		breadcrumbs = [
		utilities_breadcrumb(),
		'stock_take'
		]
		return breadcrumbs

	def form_valid(self, form):
		'''Take the uploaded inventory.csv and produce a HTML output comparing the uploaded document with the current database.'''
		file = form.save(commit=True)
		Containers = Container.objects.filter(is_empty=False)
		stock_to_url = str(file.file).split('/')[-1].split('.txt')[0]
		url = reverse('results', kwargs={'stock': str(file.id)})
		return redirect(url)		

class InventoryResultsView(BreadcrumbsMixin, DetailView):
	template_name = 'stock_results.html'	
	context_object_name = 'results'
	model = stock_take

	def get_object(self):
		"""Return the specific chemical by its id"""
		pk = self.kwargs['stock']
		stock = stock_take.objects.get(id=pk)
		return stock

	def breadcrumbs(self):
		return stock_breadcrumbs(self.object)
	
	def calculate_results(self):
		stock = self.get_object()
		uploaded_file_name = str(stock.file)
		containers = Container.objects.all()
		
		#Iterate over containers that are not empty to form a list of container id's
		database = []
		for item in containers:
			database.append(item.id)

		#Create actual list from uploaded file and run comparison
		file_upload = settings.BASE_DIR + '/' + settings.MEDIA_ROOT + '/' + uploaded_file_name
		actual = ir.create_barcode_actual(str(file_upload))
		accounted_for, not_in_db, not_in_actual = ir.analyse(actual, database)
		
		#In order: accounted_for, not_in_db_but_empty, not_in_db, not_in_actual 
		return Container.objects.filter(id__in=accounted_for), Container.objects.filter(id__in=not_in_db), not_in_db, Container.objects.filter(id__in=not_in_actual, is_empty=False)
	
	def get_context_data(self, **kwargs):
		'''Retreives the previously uploaded filename from the URL and produces results based on the current inventory.'''
		context = super().get_context_data(**kwargs)
#		if self.request.GET.get('stock') is not None:
		stock = self.get_object()
		uploaded_file_name = str(stock.file)
		containers = Container.objects.all()
		
		#Iterate over containers that are not empty to form a list of container id's
		database = []
		for item in containers:
			database.append(item.id)

		#Create actual list from uploaded file and run comparison
		file_upload = '{0}/{1}/{2}'.format(settings.BASE_DIR, settings.MEDIA_ROOT, uploaded_file_name)
		actual = ir.create_barcode_actual(str(file_upload))
		accounted_for, not_in_db, not_in_actual = ir.analyse(actual, database)
		
		#Provide context data for presentation of results
		context['accounted_for'] = Container.objects.filter(id__in=accounted_for)
		context['not_in_db_but_empty'] = Container.objects.filter(id__in=not_in_db)
		context['not_in_db'] = not_in_db
		context['not_in_actual'] = Container.objects.filter(id__in=not_in_actual, is_empty=False)
		context['csv_available'] = hasattr(self, 'write_csv')
		context['active_stock'] = stock
		return context

	def get(self, request, *args, **kwargs):
		format = request.GET.get('format')
		list = request.GET.get('list')
		if format == 'csv':
			response = HttpResponse(content_type='text/csv')
			disposition = 'attachment; filename="{}.csv"'.format(list)
			response['Content-Disposition'] = disposition
			self.write_csv(response, list)
		else:
			response = super().get(request, *args, **kwargs)
		return response

	def write_csv(self, response, list):
		writer = csv.writer(response)
		if list == 'not_in_database':
			writer.writerow(['Barcode Number'])
			for barcode_number in self.calculate_results()[2]:
				writer.writerow([barcode_number])
			return response
		if list == 'marked_as_empty':
			writer.writerow([
				'Barcode Number',
				'Chemical Name',
				'Location',
				'Owner'
				])
			for container in self.calculate_results()[1]:
				writer.writerow([
					container.id,
					container.chemical.name,
					container.location,
					container.owner.get_full_name(),
					])
			return response
		if list == 'not_scanned':
			writer.writerow([
				'Barcode',
				'Chemical Name',
				'Batch',
				'Location',
				'Container',
				'Owner',
				])
			for container in self.calculate_results()[3]:
				writer.writerow([
					container.id,
					container.chemical.name,
					container.batch,
					container.location,
					container.container_type,
					container.owner.get_full_name(),
					])
			return response

def send_stock_email(request, stock):
	"""Pass information from the javascript request to recalculate the stock take results before calling the send_email() function."""
	stock = stock_take.objects.get(id=stock)
	stock.email_results()
	return JsonResponse({'status': 'success'})

def send_email(template_name, payload):
	'''Emails all active users from the gmail set up for the server. Text is the primary format but alternative html is rendered and sent as well.'''
	active_users = User.objects.filter(is_active=True)
	active_users_email = []
	for user in active_users:
		active_users_email.append(user.email)	
	send_templated_mail(
		template_name=template_name,
        from_email='Cabana Server',
        recipient_list=active_users_email,
		context = payload,
        template_suffix="html",
)

	return JsonResponse({'status': 'success'})

# Browseable API viewsets
# =======================
class StockViewSet(viewsets.ModelViewSet):
    """Viewset for the stock_take model. User is required to be logged in to
    post."""
    # Determine which object to list
    queryset = stock_take.objects.all()
    # Decide how to convert to JSON
    serializer_class = StockSerializer
    # Require user be logged in to post to this endpoint
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
