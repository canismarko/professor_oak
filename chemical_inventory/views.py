from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView

from .models import Chemical, Container

def main(request):
    """This view function returns a generic landing page response."""
    # A 'context' is the data that the template can use
    context = {'inventory_size': 0}
    # Now put the context together with a template
    # Look in chemical_inventory/templates/main.html for the actual html
    # 'request' is the HTTP request submitted by the browser
    return render(request, 'main.html', context)

class ChemicalListView(ListView):
    """View shows a list of currently available chemicals."""

    template_name = 'chemical_list.html'

    def get_queryset(self):
        """Return the list of chemicals. The parent class (ListView) handles
        the rest."""
        qs = Chemical.objects.all()
        return qs


class ChemicalDetailView(DetailView):
    """This view shows detailed information about one chemical. Also gets
    the list of containers that this chemical is in."""

    template_name = 'chemical_detail.html'
    template_object_name = 'chemical'

    def get_object(self):
        """Return the specific chemical by its primary key ('pk')."""
        # Find the primary key from the url
        pk = self.kwargs['pk']
        # Get the actual Chemical object
        chemical = Chemical.objects.get(pk=pk)
        return chemical

    def get_context_data(self, *args, **kwargs):
        chemical = self.get_object()
        # Get the default context
        context = super().get_context_data(*args, **kwargs)
        # Add list of containers to context
        context['container_list'] = chemical.container_set.all()
        return context


class AddContainerView(CreateView):
    template_name = 'container_form.html'
    model = Container
    fields = ['chemical', 'location', 'batch', 'date_opened', 'expiration_date',
              'state', 'container_type', 'owner', 'quantity', 'unit_of_measure',
              'supplier']

    @property
    def success_url(self):
        # Look up the url for the chemical that this inventory belongs to
        url = reverse('chemical_detail', kwargs={'pk': self.object.chemical.pk})
        return url

    @success_url.setter
    def success_url(self, url):
        # Django throws an error if it can't set success_url
        pass
