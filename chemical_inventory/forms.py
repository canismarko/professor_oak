from django import forms
from djng.forms import fields as ngfields, NgFormValidationMixin, NgModelFormMixin, NgModelForm, NgForm
from djng.styling.bootstrap3.forms import Bootstrap3FormMixin

from . import models


class DateInput(forms.widgets.DateInput):
    """Widget that Renders as htlm5 <input type="date">"""
    # Suggestion taken from https://code.djangoproject.com/ticket/21470
    input_type = 'date'
    format_key = 'DATE_INPUT_FORMATS'


class ContainerForm(Bootstrap3FormMixin, NgModelFormMixin,
                    NgFormValidationMixin, NgModelForm):
    scope_prefix = 'container'
    form_name = 'container_form'
    location = ngfields.ModelChoiceField(label="Location (SDS § 7)",
                                         queryset=models.Location.objects.order_by('name'))
    date_opened = ngfields.DateField(widget=DateInput(),
                                  required=False)
    expiration_date = ngfields.DateField(widget=DateInput())
    state = ngfields.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Solid, liquid, foil, etc.'}))
    unit_of_measure = ngfields.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'g, mL, etc'}),
        required=False
    )
    batch = ngfields.CharField(label='Batch/Lot Number', required=False)
    container_type = ngfields.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Glass bottle, metal pouch, etc.'}
    ))
    class Meta:
        model = models.Container
        fields = ['location', 'batch', 'date_opened', 'expiration_date',
                  'state', 'container_type', 'quantity', 'unit_of_measure',
                  'supplier', 'comment']


class SupportingDocumentForm(NgModelFormMixin, NgFormValidationMixin,
                             Bootstrap3FormMixin, NgModelForm):
    form_name = 'supporting_document_form'
    comment = ngfields.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': '3'})
        )
    
    class Meta:
        model = models.SupportingDocument
        fields = ['name', 'file', 'comment']


# Insert "none" value into list of options
NFPA_RATINGS = [('', '----------')] + models.Chemical.NFPA_RATINGS
NFPA_HAZARDS = [('', '----------')] + models.Chemical.NFPA_HAZARDS

# class GHSSymbolWidget(forms.Widget):
    # def __init__(self, ngmodel="", *args, **kwargs):
    #     self.ngmodel = ngmodel
    #     return super().__init__(*args, **kwargs)
    # formname="chemical_form", modelname="ghs_hazards"

    # def render(self, *args, **kwargs):
    #     form_name = self.attrs.pop('ow-form', "")
    #     s = '<div ghs-symbol-picker id="{id}" ow-form="{form_name}"></div>'
    #     return s.format(form_name=form_name, **kwargs['attrs'])


class ChemicalForm(NgModelFormMixin, NgFormValidationMixin,
                   Bootstrap3FormMixin, NgModelForm):
    # class ChemicalForm(forms.ModelForm):
    scope_prefix = 'chemical'
    form_name = 'chemical_form'
    cas_number = ngfields.CharField(
        label="CAS Number (SDS § 1)",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'eg. 7732-18-5'}))
    formula = ngfields.CharField(
        label="Formula (SDS § 3)",
        required=False,
        # widget=forms.TextInput(attrs={'placeholder': 'eg. H_2O', 'ow-formula': 'ow-formula'})
    )
    ghs_hazards = ngfields.ModelMultipleChoiceField(
        label="GHS Hazards (SDS § 2)",
        # widget=forms.SelectMultiple(attrs={'ow-form': 'chemical_form'}),
        queryset=models.Hazard.objects.all(),
        required=False)
    health = ngfields.ChoiceField(
        label="Health NFPA Rating (SDS § 15 or 16)",
        choices=NFPA_RATINGS)
    flammability = ngfields.ChoiceField(
        label="Flammability NFPA Rating (SDS § 15 or 16)",
        choices=NFPA_RATINGS)
    instability = ngfields.ChoiceField(
        label="Instability NFPA Rating (SDS § 15 or 16)",
        choices=NFPA_RATINGS)
    special_hazards = ngfields.ChoiceField(
        label="Special Hazards (SDS § 15 or 16)",
        choices=NFPA_HAZARDS, required=False)
    gloves = ngfields.ModelMultipleChoiceField(
        label="Gloves (SDS § 8.2)",
        queryset=models.Glove.objects.all())
    safety_data_sheet = ngfields.FileField(
        label="Safety Data Sheet (MSDS)",
        widget=forms.FileInput(attrs={'file-model': 'chemical.safety_data_sheet'}),
        required=False)
    class Meta:
        model = models.Chemical
        fields = ['name', 'cas_number', 'formula', 'ghs_hazards',
                  'health', 'flammability', 'instability', 'special_hazards',
                  'gloves', 'safety_data_sheet']


class GloveForm(Bootstrap3FormMixin, NgModelFormMixin,
                NgFormValidationMixin, NgModelForm):
    scope_prefix = 'glove'
    form_name = 'glove_form'
    class Meta:
        model = models.Glove
        fields = ['name']

class SupplierForm(Bootstrap3FormMixin, NgModelFormMixin,
                   NgFormValidationMixin, NgModelForm):
    scope_prefix = 'supplier'
    form_name = 'supplier_form'
    class Meta:
        model = models.Supplier
        fields = ['name']
