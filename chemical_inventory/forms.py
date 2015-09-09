from djangular.forms import NgModelFormMixin, NgModelForm

from . import models

class ContainerForm(NgModelFormMixin, NgModelForm):
    class Meta:
        model = models.Container
        fields = ['chemical', 'location', 'batch', 'date_opened', 'expiration_date',
              'state', 'container_type', 'quantity', 'unit_of_measure',
              'supplier']

class ChemicalForm(NgModelFormMixin, NgModelForm):
    class Meta:
        model = models.Chemical
        fields = ['name', 'cas_number', 'formula',
                  'health', 'flammability', 'instability', 'special_hazards',
                  'glove']
