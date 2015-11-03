from django import forms
from djangular.forms import NgFormValidationMixin, NgModelFormMixin, NgModelForm, NgForm
from djangular.styling.bootstrap3.forms import Bootstrap3FormMixin
from django.core.validators import RegexValidator
from django.forms.widgets import DateTimeInput
from . import models

class ULONtemplateForm(NgModelFormMixin, NgFormValidationMixin, Bootstrap3FormMixin, NgModelForm):
    form_name = 'ulon_template'
    
    list_of_hazards = ["Biohazard",
                        "Flammable Gas",
                        "Mutagen",
                        "Shock Sensitive",
                        "Carcinogen",
                        "Flammable Liquid",
                        "Noise",
                        "Teratogen"
                        "Compressed Gas"
                        "Flammable Solid",
                        "Organic Peroxide",
                        "Toxic",
                        "Corrosive",
                        "Highly Toxic",
                        "Oxidizer",
                        "Unstable",
                        "Cryogen",
                        "Hot Oil Bath",
                        "Pyrophoric",
                        "UV Light",
                        "Electrical",
                        "Hot Plate",
                        "Reaction Under Pressure",
                        "Water Reactive",
                        "Explosive",
                        "Irritant",
                        "Heating",
                        "Flammable",
                        "Laser",
                        "Running Water",
                        "Aerosol",
                        "Magnetic Field",
                        "X-Ray",
                        "Moving Parts"
                        ]
    
    #Validators
    contact_regex = RegexValidator(regex=r'^[0-9]{3}-[0-9]{3}-[0-9]{4}$', message="Phone number must be entered in the format: '999-999-9999'.")
    
    #Fields
    experiment_start = forms.DateField(widget=DateTimeInput(), required=True)
    experiment_end = forms.DateField(widget=DateTimeInput(), required=True)
    contact_number = forms.CharField(validators=[contact_regex], required=True, max_length=12,
        widget=forms.TextInput(
        attrs={'placeholder': 'e.g. 999-999-9999'}
    ))
    experiment_description = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'rows': '3'})
        ) 
    experiment_location = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': '4169, 4130...'}))
    emergency_shutdown = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'rows': '3'})
        )
    hazards = forms.ModelMultipleChoiceField(queryset=list_of_hazards, widget=forms.SelectMultiple)
    class Meta:
        fields = ['experiment_start', 'experiment_end', 'contact_number', 'experiment_description', 'experiment_location', 'emergency_shutdown', 'hazards']