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
from django.http import HttpResponseRedirect

from .forms import ChemicalForm, ContainerForm, GloveForm, SupplierForm
from .models import Chemical, Container, Glove, Supplier
import xkcd
from .serializers import ChemicalSerializer, ContainerSerializer, GloveSerializer, SupplierSerializer


def main(request):
    """This view function returns a generic landing page response."""
    # A 'context' is the data that the template can use
    comic = xkcd.Comic(xkcd.getLatestComicNum())
    context = {
    'inventory_size': Container.objects.filter(is_empty=False).count(),
    'xkcd_url': comic.getImageLink(),
    'xkcd_alt': comic.getAsciiAltText(),
    'xkcd_title': comic.getAsciiTitle()
    }
    # Now put the context together with a template
    # Look in chemical_inventory/templates/main.html for the actual html
    # 'request' is the HTTP request submitted by the browser
    return render(request, 'main.html', context)

class ChemicalListView(ListView):
    """View shows a list of currently available chemicals."""

    template_name = 'chemical_list.html'
    model = Chemical


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
        container_list = chemical.container_set.order_by('is_empty', 'expiration_date')
        context['container_list'] = container_list
        return context

class AddContainerView(TemplateView):
    template_name = 'container_add.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # Load the angular forms for container and chemical
        context.update(chemical_form=ChemicalForm())
        context.update(container_form=ContainerForm())
        context.update(glove_form=GloveForm())
        context.update(supplier_form=SupplierForm())
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
    fields = ['cas_number', 'name', 'formula', 'health', 'flammability', 'instability', 'special_hazards', 'gloves', 'safety_data_sheet'] 
    def get_object(self):
        """Return the specific chemical by its primary key ('pk')."""
        # Find the primary key from the url
        pk = self.kwargs['pk']
        # Get the actual Chemical object
        chemical = Chemical.objects.get(pk=pk)
        return chemical

    def form_valid(self,form):
        obj = form.save(commit=False)
        obj.author = self.request.user
        obj.save()
        return HttpResponseRedirect(self.get_success_url())

class EditContainerView(UpdateView):
    template_name = 'container_edit.html'
    model = Container
    fields = ['chemical', 'location', 'batch', 'date_opened', 'expiration_date','state', 'container_type', 'owner', 'quantity', 'unit_of_measure','supplier', 'is_empty'] 

    def get_object(self):
        """Return the specific chemical by its primary key ('pk')."""
        # Find the primary key from the url
        pk = self.kwargs['pk']
        # Get the actual Chemical object
        container = Container.objects.get(pk=pk)
        return container


# Browseable API viewsets
# =======================
class SupplierViewSet(viewsets.ModelViewSet):
    """Viewset for the Chemical model. User is required to be logged in to
    post."""
    # Determine which object to list
    queryset = Supplier.objects.all()
    # Decide how to convert to JSON
    serializer_class = SupplierSerializer
    # Require user be logged in to post to this endpoint
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class GloveViewSet(viewsets.ModelViewSet):
    """Viewset for the Chemical model. User is required to be logged in to
    post."""
    # Determine which object to list
    queryset = Glove.objects.all()
    # Decide how to convert to JSON
    serializer_class = GloveSerializer
    # Require user be logged in to post to this endpoint
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


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
        # (Copied from rest_framework.mixins with modification)
        data = request.data.copy()
        # Set the owner to be the request user
        data['owner'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
