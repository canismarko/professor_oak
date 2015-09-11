from djangular.forms import NgFormValidationMixin, NgModelFormMixin, NgModelForm
from djangular.styling.bootstrap3.forms import Bootstrap3FormMixin

from . import models

class ContainerForm(Bootstrap3FormMixin, NgModelFormMixin, NgFormValidationMixin, NgModelForm):
    scope_prefix = 'container'
    form_name = 'container_form'
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
