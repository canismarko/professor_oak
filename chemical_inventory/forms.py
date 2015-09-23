from django import forms
from djangular.forms import NgFormValidationMixin, NgModelFormMixin, NgModelForm
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
    date_opened = forms.DateField(widget=DateInput())
    expiration_date = forms.DateField(widget=DateInput())
    class Meta:
        model = models.Container
        fields = ['location', 'batch', 'date_opened', 'expiration_date',
                  'state', 'container_type', 'quantity', 'unit_of_measure',
                  'supplier']


class ChemicalForm(Bootstrap3FormMixin, NgModelFormMixin, NgFormValidationMixin, NgModelForm):
    scope_prefix = 'chemical'
    form_name = 'chemical_form'
    class Meta:
        model = models.Chemical
        fields = ['name', 'cas_number', 'formula',
                  'health', 'flammability', 'instability', 'special_hazards',
                  'glove']

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
