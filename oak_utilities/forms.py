from django import forms
from djangular.forms import NgFormValidationMixin, NgModelFormMixin, NgModelForm, NgForm
from djangular.styling.bootstrap3.forms import Bootstrap3FormMixin
from django.core.validators import RegexValidator
from django.forms.widgets import DateTimeInput
from . import models

class DateInput(forms.widgets.DateInput):
    """Widget that Renders as htlm5 <input type="date">"""
    # Suggestion taken from https://code.djangoproject.com/ticket/21470
    input_type = 'date'
    format_key = 'DATE_INPUT_FORMATS'

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
        label="Start Date",
        widget=DateInput(),
        required=True)
    experiment_end = forms.DateField(
        label="End Date",
        widget=DateInput(),
        required=True)
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
        label = "Hazards (Ctrl+click to select multiple)",
        choices=sorted(list_of_hazards, key=getKey),
        # widget=forms.CheckboxSelectMultiple(), 
        required=False
        )
    additional_hazards = forms.CharField(
        label="Additional Hazards (if any)",
        required=False,
        widget=forms.Textarea(attrs={'rows': '3'})
         ) 
    class Meta:
        fields = ['experiment_start', 'experiment_end', 'contact_number', 'chemicals', 'experiment_description', 'experiment_location', 'experiment_sublocation', 'emergency_shutdown', 'hazards', 'additional_hazards']