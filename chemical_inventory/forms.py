from django import forms
from djangular.forms import NgFormValidationMixin, NgModelFormMixin, NgModelForm, NgForm
from djangular.styling.bootstrap3.forms import Bootstrap3FormMixin

from . import models


class DateInput(forms.widgets.DateInput):
    """Widget that Renders as htlm5 <input type="date">"""
    # Suggestion taken from https://code.djangoproject.com/ticket/21470
    input_type = 'date'
    format_key = 'DATE_INPUT_FORMATS'


class ContainerForm(Bootstrap3FormMixin, NgModelFormMixin, NgFormValidationMixin, NgModelForm):
    scope_prefix = 'container'
    form_name = 'container_form'
    location = forms.ModelChoiceField(label="Location (SDS § 7)",
                                      queryset=models.Location.objects.all())
    date_opened = forms.DateField(widget=DateInput(),
                                  required=False)
    expiration_date = forms.DateField(widget=DateInput())
    state = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Solid, liquid, foil, etc.'}))
    unit_of_measure = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'g, mL, etc'}),
                                      required=False)
    batch = forms.CharField(label='Batch/Lot Number', required=False)
    container_type = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Glass bottle, metal pouch, etc.'}
    ))
    class Meta:
        model = models.Container
        fields = ['location', 'batch', 'date_opened', 'expiration_date',
                  'state', 'container_type', 'quantity', 'unit_of_measure',
                  'supplier', 'comment']


# Insert "none" value into list of options
NFPA_RATINGS = [('', '----------')] + models.Chemical.NFPA_RATINGS
NFPA_HAZARDS = [('', '----------')] + models.Chemical.NFPA_HAZARDS

class ChemicalForm(NgModelFormMixin, NgFormValidationMixin, Bootstrap3FormMixin, NgModelForm):
    scope_prefix = 'chemical'
    form_name = 'chemical_form'
    cas_number = forms.CharField(
        label="CAS Number (SDS § 1)",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'eg. 7732-18-5'}))
    formula = forms.CharField(
        label="Formula (SDS § 3)",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'eg. H_2O'}))
    health = forms.ChoiceField(
        label="Health NFPA Rating (SDS § 15 or 16)",
        choices=NFPA_RATINGS)
    flammability = forms.ChoiceField(
        label="Flammability NFPA Rating (SDS § 16)",
        choices=NFPA_RATINGS)
    instability = forms.ChoiceField(
        label="Instability NFPA Rating (SDS § 16)",
        choices=NFPA_RATINGS)
    special_hazards = forms.ChoiceField(
        label="Special Hazards (SDS § 16)",
        choices=NFPA_HAZARDS, required=False)
    gloves = forms.ModelMultipleChoiceField(
        label="Gloves (SDS § 8.2)",
        queryset=models.Glove.objects.all())
    safety_data_sheet = forms.FileField(
        label="Safety Data Sheet (MSDS)",
        widget=forms.FileInput(attrs={'file-model': 'chemical.safety_data_sheet'}))
    class Meta:
        model = models.Chemical
        fields = ['name', 'cas_number', 'formula',
                  'health', 'flammability', 'instability', 'special_hazards',
                  'gloves', 'safety_data_sheet']


class GloveForm(Bootstrap3FormMixin, NgModelFormMixin, NgFormValidationMixin, NgModelForm):
    scope_prefix = 'glove'
    form_name = 'glove_form'
    class Meta:
        model = models.Glove
        fields = ['name']

class SupplierForm(Bootstrap3FormMixin, NgModelFormMixin, NgFormValidationMixin, NgModelForm):
    scope_prefix = 'supplier'
    form_name = 'supplier_form'
    class Meta:
        model = models.Supplier
        fields = ['name']
