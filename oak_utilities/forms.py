from django import forms
from djangular.forms import NgFormValidationMixin, NgModelFormMixin, NgModelForm, NgForm
from djangular.styling.bootstrap3.forms import Bootstrap3FormMixin
from django.core.validators import RegexValidator
from django.forms.widgets import DateTimeInput, TimeInput, SplitDateTimeWidget

from django.contrib.admin.widgets import AdminDateWidget
# from bootstrap3_datetime.widgets import DateTimePicker
from . import models
from django.conf import settings
import datetime
from functools import partial

DateInput = partial(forms.DateInput, {'class': 'datepicker'})

class DateRangeForm(forms.Form):
	start_date = forms.DateField(widget=DateInput())
	end_date = forms.DateField(widget=DateInput())

#class DateInput(forms.widgets.DateInput):
#	"""Widget that Renders as htlm5 <input type="date">"""
#	# Suggestion taken from https://code.djangoproject.com	icket/21470
#	input_type = 'date'
#	format_key = 'DATE_INPUT_FORMATS'

class TimeInput(forms.widgets.TimeInput):
	"""Widget that aids time picking"""
	input_type = 'time'
	format_key = 'TIME_INPUT_FORMATS'
	
class DateTimeInput(forms.widgets.DateTimeInput):
	input_type = 'datetime'
	format_key = 'DATETIME_INPUT_FORMATS'
	
class CheckboxChoiceInput(forms.widgets.CheckboxChoiceInput):
	input_type = 'radio'
	
class ULONtemplateForm(NgFormValidationMixin, Bootstrap3FormMixin, NgForm):
	form_name = 'ulon_template'
	
	def getKey(item):
		return item[1]
	
	list_of_hazards = (
						("Biohazard","Biohazard"),
						("FlammableGas","Flammable Gas"),
						("Mutagen","Mutagen"),
						("ShockSensitive","Shock Sensitive"),
						("Carcinogen","Carcinogen"),
						("FlammableLiquid","Flammable Liquid"),
						("Noise","Noise"),
						("Teratogen","Teratogen"),
						("CompressedGas","Compressed Gas"),
						("FlammableSolid","Flammable Solid"),
						("OrganicPeroxide","Organic Peroxide"),
						("Toxic","Toxic"),
						("Corrosive","Corrosive"),
						("HighlyToxic","Highly Toxic"),
						("Oxidizer","Oxidizer"),
						("Unstable","Unstable"),
						("Cryogen","Cryogen"),
						("HotOilBath","Hot Oil Bath"),
						("Pyrophoric","Pyrophoric"),
						("UVLight","UV Light"),
						("Electrical","Electrical"),
						("HotPlate","Hot Plate"),
						("ReactionUnderPressure","Reaction Under Pressure"),
						("WaterReactive","Water Reactive"),
						("Explosive","Explosive"),
						("Irritant","Irritant"),
						("Heating","Heating"),
						("Flammable","Flammable"),
						("Laser","Laser"),
						("RunningWater","Running Water"),
						("Aerosol","Aerosol"),
						("MagneticField","Magnetic Field"),
						("XRay","X-Ray"),
						("MovingParts","Moving Parts")
						)
	
	#Validators
	contact_regex = RegexValidator(regex=r'^[0-9]{3}-[0-9]{3}-[0-9]{4}$', message="Phone number must be entered in the format: '999-999-9999'.")
	
	#Fields

	experiment_start = forms.DateField(
		widget=DateInput(),
		required = True
		)
	experiment_start_time = forms.TimeField(
		label="Start Time",
		widget=TimeInput(format="%H:%M"),
		required=False)
	experiment_end = forms.DateField(
		widget=DateInput(),
		required = True
		)
	experiment_end_time = forms.TimeField(
		label="End Time",
		widget=TimeInput(format="%H:%M"),
		required=False)
	contact_number = forms.CharField(
		validators=[contact_regex],
		required=True,
		max_length=12,
		label="Contact Number",
		widget=forms.TextInput(
		attrs={'placeholder': 'e.g. 999-999-9999'})
		)
	chemicals = forms.CharField(
		label="Chemicals in use",
		required=True,
		widget=forms.Textarea(
		attrs={'placeholder': 'e.g. Lithium Hydroxide, Carbon', 'rows': '3'})
		) 
	experiment_description = forms.CharField(
		label="Experiment Description",
		required=True,
		widget=forms.Textarea(attrs={'rows': '3'})
		) 
	experiment_location = forms.CharField(
		label="Room Number & Building",
		required=True, 
		widget=forms.TextInput(attrs={'placeholder': '4169 SES, 4130 SES...'}))
	experiment_sublocation = forms.CharField(
		label="Sublocation (if any)",
		required=False, 
		widget=forms.TextInput(attrs={'placeholder': 'Fumehood A...'}))
	emergency_shutdown_procedure = forms.CharField(
		label="Emergency Shutdown Procedure",
		required=True, 
		widget=forms.Textarea(attrs={'rows': '3'})
		 )
	hazards = forms.MultipleChoiceField(
		label = "Hazards",
		choices=sorted(list_of_hazards, key=getKey),
		widget=forms.CheckboxSelectMultiple(
		attrs={'class':'checkbox'}), 
		required=False
		)
	additional_hazards = forms.CharField(
		label="Additional Hazards (if any)",
		required=False,
		widget=forms.Textarea(attrs={'rows': '3'})
		 )

	class Meta:
		fields = [
		'experiment_start',
		'experiment_end',
		'contact_number', 
		'chemicals', 
		'experiment_description', 
		'experiment_location', 
		'experiment_sublocation', 
		'emergency_shutdown',  
		'additional_hazards'
		]
