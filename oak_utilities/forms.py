from django import forms
from djng.forms import NgFormValidationMixin, NgModelFormMixin, NgModelForm, NgForm
from djng.styling.bootstrap3.forms import Bootstrap3FormMixin
from django.core.validators import RegexValidator
from django.forms.widgets import DateTimeInput, TimeInput, SplitDateTimeWidget
from django.forms.utils import ErrorList
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

class DateInput(forms.widgets.DateInput):
    """Widget that Renders as htlm5 <input type="date">"""
    # Suggestion taken from https://code.djangoproject.com/ticket/21470
    input_type = 'date'
    format_key = 'DATE_INPUT_FORMATS'

class TimeInput(forms.widgets.TimeInput):
    """Widget that aids time picking"""
    input_type = 'time'
    format_key = 'TIME_INPUT_FORMATS'
    
class DateTimeInput(forms.widgets.DateTimeInput):
    input_type = 'datetime'
    format_key = 'DATETIME_INPUT_FORMATS'
    
class CheckboxChoiceInput(forms.widgets.CheckboxChoiceInput):
    input_type = 'radio'
    
class ULONtemplateForm(Bootstrap3FormMixin, NgModelFormMixin,
            NgFormValidationMixin, NgModelForm):
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
        label="Start Date",
        # widget=DateTimePicker(options={"format": "YY-MM-DD HH:mm", "pickSeconds": False}),
        widget=DateInput(),
        required=True)
    experiment_start_time = forms.TimeField(
        label="Start Time",
        widget=TimeInput(format="%H:%M",
        attrs={'placeholder': 'e.g. 09:00, 12:00, 14:00'}),
        required=False,
        )
    experiment_end = forms.DateField(
        label="End Date",
        widget=DateInput(),
        required=True)
    experiment_end_time = forms.TimeField(
        label="End Time",
        widget=TimeInput(format="%H:%M",
        attrs={'placeholder': 'e.g. 09:00, 12:00, 14:00'}),
        required=False,
        )
    contact_number = forms.CharField(
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
        label = "Hazards (select all that apply)",
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
        model = models.ULON
        fields = [
        'experiment_start',
        'experiment_start_time',
        'experiment_end',
        'experiment_end_time',
        'contact_number', 
        'chemicals', 
        'experiment_description', 
        'experiment_location', 
        'experiment_sublocation', 
        'emergency_shutdown_procedure',  
        'hazards',
        'additional_hazards'
        ]

class UploadInventoryForm(forms.ModelForm):
    form_name = 'stock_take'
    file = forms.FileField(
        label = '',
        required = True,
        )

    class Meta:
        model = models.stock_take
        fields = ['file']       
    
    def clean(self):
        cleaned_data = super(UploadInventoryForm, self).clean()
        try:
            for line in cleaned_data.get("file").readlines():
                try:
                    int(line)
                except ValueError:
                    self._errors['file'] = ErrorList(["This file could not be read, please make sure the file is a single list of integers, each integer corresponding to a barcode."])
                    raise forms.ValidationError('Non-integers found, file not saved.')
        except AttributeError:
                self._errors['file'] = ErrorList(["No file found. Make sure you use the upload button above to find your stock take file."])
                raise forms.ValidationError('No file found.')
        return self.cleaned_data
