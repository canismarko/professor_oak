from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView
from rest_framework import viewsets, permissions, response, status
from django.utils.safestring import mark_safe

from .forms import ChemicalForm, ContainerForm
from .models import Chemical, Container
import xkcd
from .serializers import ChemicalSerializer, ContainerSerializer


def main(request):
    """This view function returns a generic landing page response."""
    # A 'context' is the data that the template can use
    context = {
	'inventory_size': len(Container.objects.filter(empty_status=False)),
	'xkcd_url': xkcd.Comic(xkcd.getLatestComicNum()).getImageLink(),
	'xkcd_alt': xkcd.Comic(xkcd.getLatestComicNum()).getAsciiAltText(),
	'xkcd_title': xkcd.Comic(xkcd.getLatestComicNum()).getAsciiTitle()
	}
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

class AddContainerView(TemplateView):
    template_name = 'container_form.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # Load the angular forms for container and chemical
        context.update(chemical_form=ChemicalForm())
        context.update(container_form=ContainerForm())
        return context

    @property
    def success_url(self):
        # Look up the url for the chemical that this inventory belongs to
        url = reverse('chemical_detail', kwargs={'pk': self.object.chemical.pk})
        return url

    @success_url.setter
    def success_url(self, url):
        # Django throws an error if it can't set success_url
        pass


class EditChemicalView(UpdateView):
	template_name = 'chemical_edit.html'
	template_object_name = Chemical
	model = Chemical
	fields = ['cas_number', 'name', 'formula', 'health', 'flammability', 'instability', 'special_hazards', 'glove'] 

	# Do I have to do this again here?
	def get_object(self):
		"""Return the specific chemical by its primary key ('pk')."""
		# Find the primary key from the url
		pk = self.kwargs['pk']
		# Get the actual Chemical object
		chemical = Chemical.objects.get(pk=pk)
		return chemical

class EditContainerView(UpdateView):
    template_name = 'container_edit.html'
    model = Container
    fields = ['chemical', 'location', 'batch', 'date_opened', 'expiration_date','state', 'container_type', 'owner', 'quantity', 'unit_of_measure','supplier', 'empty_status'] 

	# Do I have to do this again here?
    def get_object(self):
        """Return the specific chemical by its primary key ('pk')."""
        # Find the primary key from the url
        pk = self.kwargs['pk']
        # Get the actual Chemical object
        container = Container.objects.get(pk=pk)
        return container

# Browseable API viewsets
# =======================

class ChemicalViewSet(viewsets.ModelViewSet):
    """Viewset for the Chemical model. User is required to be logged in to
    post."""
    # Determine which object to list
    queryset = Chemical.objects.all()
    # Decide how to convert to JSON
    serializer_class = ChemicalSerializer
    # Require user be logged in to post to this endpoint
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class ContainerViewSet(viewsets.ModelViewSet):
    """Viewset for the Chemical model. User is required to be logged in to
    post."""
    # Determine which object to list
    queryset = Container.objects.all()
    # Decide how to convert to JSON
    serializer_class = ContainerSerializer
    # Require user be logged in to post to this endpoint
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def create(self, request, *args, **kwargs):
        # Copied from rest_framework.mixins with modification
        data = request.data.copy()
        data['owner'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
