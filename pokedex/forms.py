#pokedex/forms.py
import datetime

from django import forms
from image_cropping import ImageCropWidget
from braces.forms import UserKwargModelFormMixin
from django.contrib.admin.widgets import AdminDateWidget
from django.forms.utils import ErrorList

from . import models
from functools import partial

DateInput = partial(forms.DateInput, {'class': 'datepicker'})

class DateRangeForm(forms.Form):
	start_date = forms.DateField(widget=DateInput())
	end_date = forms.DateField(widget=DateInput())

class SampleForm(UserKwargModelFormMixin, forms.ModelForm):
	scope_prefix = 'sample'
	form_name = 'sample_form'
	required_css_class = 'required'
	#user_project = models.Project.objects.all().filter(user_id = request.get.user)

	sample_number = forms.CharField(
		label='Sample ID',
		max_length=10,
		required=True,
		widget=forms.TextInput(
			attrs={
				'placeholder': 'e.g. LCO123'
				})
		)
	name = forms.CharField(
		max_length=200,
		required=True,
		widget=forms.TextInput(
			attrs={
				'placeholder': 'e.g. Lithium Cobalt Oxide'
				})
		)
	formula = forms.CharField(
		label = 'Formula',
		max_length=50,
		required=False,
		widget=forms.TextInput(
			attrs={
				'placeholder': 'Custom Markup Supported'
				})
		)
	experiment_variable = forms.FloatField(
		label='Variable (rpm/oC/etc.)',
		required=True
		)
	experiment_time = forms.FloatField(
		label='Time (h)',
		required=True
		)
	experiment_equation = forms.CharField(
		label='Stoichiometric Equation',
		max_length=200,
		required=False,
		widget=forms.Textarea(
			attrs={
				'rows':1,
				'cols':40,
				'style': 'height: 2.25em;',
				'placeholder': 'LaTeX Supported'
			})
		)
	start_date = forms.DateField(
		widget=DateInput(),
		required = False
		)
	end_date = forms.DateField(
		widget=DateInput(),
		required = False
		)
	associated_project = forms.ModelMultipleChoiceField(
		widget=forms.CheckboxSelectMultiple(),
		queryset=models.Project.objects.all(),
		required=True)
	comment = forms.CharField(
		label='Comment',
		required=False,
		widget=forms.Textarea(
			attrs={
				'placeholder': 'e.g. Sample turned from black to blue after heating.'
			})
		)
	file_XRD = forms.FileField(
		label = 'XRD Image File',
		required = False,
		)
	file_EC = forms.FileField(
		label = 'Electrochemistry Image File',
		required = False,
		)
	file_TEM = forms.FileField(
		label = 'TEM Image File',
		required = False,
		)
	file_TGA = forms.FileField(
		label = 'TGA Image File',
		required = False,
		)
	file_XAS = forms.FileField(
		label = 'XAS Image File',
		required = False,
		)

	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop("request", None)		
		super(SampleForm, self).__init__(*args, **kwargs)
		#get projects associated with current user
		user_project = models.User_Project.objects.all().filter(user = self.request)
		#find project objects
		projects = models.Project.objects.all().filter(is_archived = False, user_project = user_project)
		self.fields['associated_project'].queryset = projects
		#for key in self.fields:
		#	pass

	def clean(self):
		super(SampleForm, self).clean()
		start_date = self.cleaned_data.get("start_date")	
		end_date = self.cleaned_data.get("end_date")

		if end_date and start_date:
			if end_date < start_date:
				self._errors['end_date'] = ErrorList(["The end date can't be before the start date"])
				raise forms.ValidationError("The end date can't be before the start date")
		return self.cleaned_data

	class Meta:
		model = models.Sample
		widget = {
		'file_photo': ImageCropWidget,
		}

		fields = [
		'sample_number', 
		'name',
		'formula',
		'experiment_medium',
		'experiment_atmosphere',
		'experiment_variable',
		'experiment_time',
		'experiment_equation',
		'start_date',
		'end_date',
		'comment',
		'file_photo',
		'cropping',
		'file_XRD',
		'file_EC',
		'file_TEM',
		'file_TGA',
		'file_XAS',
		'associated_project'
		]

class SamplePhotoForm(UserKwargModelFormMixin, forms.ModelForm):
	scope_prefix = 'sample'
	form_name = 'sample_photo_form'
	required_css_class = 'required'

	class Meta:
		model = models.Sample
		widget = {
		'file_photo': ImageCropWidget,
		}

		fields = [
		'file_photo',
		'cropping'
		]
