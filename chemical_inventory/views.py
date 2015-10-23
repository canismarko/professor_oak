from collections import namedtuple

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, FormView
from rest_framework import viewsets, permissions, response, status
from django.utils.safestring import mark_safe
from django.http import HttpResponseRedirect, JsonResponse
from django.conf import settings
from django.db.models import Q, Count

from .forms import ChemicalForm, ContainerForm, GloveForm, SupplierForm, SupportingDocumentForm
from .models import Chemical, Container, Glove, Supplier, SupportingDocument
import xkcd
from .serializers import ChemicalSerializer, ContainerSerializer, GloveSerializer, SupplierSerializer


GLOSSARY_FILTERS = (
	'0..9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
)

breadcrumb = namedtuple('breadcrumb', ('name', 'url'))
def main_breadcrumb():
    return breadcrumb('Chemical Inventory', reverse_lazy('inventory_main'))

class breadcrumbs():
    """Modifies the request to include a list of ancestor pages, should be
    closely aligned with the URL. If each list item is a string, it will
    be resolved to a url, otherwise it will be treated as a tuple of
    (name, url)."""
    trail = []

    def __init__(self, trail):
        self.trail = trail

    def __call__(self, view_function):
        # This is the actual decorator
        self.view_function = view_function
        return self.set_breadcrumbs

    def set_breadcrumbs(self, request, *args, **kwargs):
        """Add data to the request indicating what the breadcrumb trail is."""
        request.breadcrumbs = self.trail
        return self.view_function(request, *args, **kwargs)


@breadcrumbs([main_breadcrumb()])
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
    glossary_filters = GLOSSARY_FILTERS

    def get_context_data(self, *args, **kwargs):
        # Get the default context
        context = super().get_context_data(*args, **kwargs)
        # Add list of glossary filters to context
        context['glossary_filters'] = self.glossary_filters
        context['active_filter'] = self.request.GET.get('filter')
        context['active_search'] = self.request.GET.get('search')
        return context

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        filterstring = self.request.GET.get('filter')
        searchstring = self.request.GET.get('search')
        # Search in name and formula
        if searchstring is not None: #ignores empty searchstring (if this ever happens)
            queryset = queryset.filter(Q(formula__icontains=searchstring) | Q(name__icontains=searchstring) | Q(stripped_formula__icontains=searchstring))
        # For leading digits
        if filterstring == '0..9':
            queryset = queryset.filter(name__regex=r'^\d').exclude(name__isnull=True)
        # For everything else
        elif filterstring is not None:  #Ignores empty returns
            queryset = queryset.filter(name__istartswith=filterstring).exclude(name__isnull=True)
        queryset = sorted(queryset, key=lambda x: x.is_in_stock(), reverse=True)
        return queryset

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

    @staticmethod
    def breadcrumbs(chemical):
        return [
            main_breadcrumb(),
            'chemical_list',
            breadcrumb(chemical.name, reverse('chemical_detail', kwargs={'pk': chemical.pk}))
        ]

    def get_context_data(self, *args, **kwargs):
        chemical = self.get_object()
        # Add breadcrumbs
        self.request.breadcrumbs = self.breadcrumbs(chemical)
        # Get the default context
        context = super().get_context_data(*args, **kwargs)
        # Add list of containers to context
        container_list = chemical.container_set.order_by('is_empty', 'expiration_date')
        context['container_list'] = container_list
        return context


class SupportingDocumentView(FormView):
    template_name = 'supporting_documents.html'
    form_class = SupportingDocumentForm

    def dispatch(self, *args, **kwargs):
        # Set container for later use
        self.container = Container.objects.get(pk=self.kwargs['container_pk'])
        return super().dispatch(*args, **kwargs)

    def get_success_url(self):
        container_pk = self.kwargs['container_pk']
        return reverse('supporting_documents',
                       kwargs={'container_pk': container_pk})

    def get_context_data(self, *args, **kwargs):
        # Set breadcrumbs
        self.request.breadcrumbs = ChemicalDetailView.breadcrumbs(self.container.chemical)
        self.request.breadcrumbs.append(('Supporting Documents',
                                         self.get_success_url()))
        # Inherit parent context
        context = super().get_context_data(*args, **kwargs)
        # Set our own context entries
        context['container'] = self.container
        context['documents'] = self.container.supportingdocument_set.order_by('-date_added')
        return context

    def form_valid(self, form):
        # Set some attributes and save container
        document = form.save(commit=False)
        document.owner = self.request.user
        document.container = self.container
        document.save()
        self.object = document
        # Redirect to new url
        return HttpResponseRedirect(self.get_success_url())


class AddContainerView(TemplateView):
    template_name = 'container_add.html'

    def get_context_data(self, *args, **kwargs):
        # Add breadcrumbs
        chemical_id = self.request.GET.get('chemical_id')
        if chemical_id is not None:
            chemical = Chemical.objects.get(pk=chemical_id)
            self.request.breadcrumbs = ChemicalDetailView.breadcrumbs(chemical)
        else:
            self.request.breadcrumbs = [main_breadcrumb()]
        self.request.breadcrumbs.append(('Add to Inventory', reverse('add_container')))
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
    form_class = ChemicalForm
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

    def get_context_data(self, *args, **kwargs):
        # Set the breadcrumb navigation
        self.request.breadcrumbs = ChemicalDetailView.breadcrumbs(self.object)
        new_breadcrumb = ('Edit', reverse('chemical_edit', kwargs={'pk': self.object.pk}))
        self.request.breadcrumbs.append(new_breadcrumb)
        return super().get_context_data(*args, **kwargs)


class EditContainerView(UpdateView):
    template_name = 'container_edit.html'
    model = Container
    form_class = ContainerForm

    def get_object(self):
        """Return the specific chemical by its primary key ('pk')."""
        # Find the primary key from the url
        pk = self.kwargs['pk']
        # Get the actual Chemical object
        container = Container.objects.get(pk=pk)
        return container

    def get_context_data(self, *args, **kwargs):
        # Set the breadcrumb navigation
        self.request.breadcrumbs = ChemicalDetailView.breadcrumbs(self.object.chemical)
        new_breadcrumb = ('Edit Container',
                          reverse('container_edit', kwargs={'pk': self.object.pk}))
        self.request.breadcrumbs.append(new_breadcrumb)
        return super().get_context_data(*args, **kwargs)


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

    # def update(self, request, *args, **kwargs):
        # data = request.data.copy()
        # if data['is_empty'] == True:
            # return response.Response(serializer.data, status=status.HTTP_400_BADREQUEST, headers=headers)
        # return super().update(*args, **kwargs)
            
@login_required
def print_label(request, container_pk):
        """Pass the information from the container to subprocess, convert it to a csv file and merge with the gLabel template."""
        # stubbed for  development 
        container = Container.objects.get(pk=container_pk)
        container.print_label()
        return JsonResponse({'status': 'success'})
        
@login_required
def get_quick_empty(request, container_pk):
        """Pass the information from the container to subprocess, convert it to a csv file and merge with the gLabel template."""
        # stubbed for  development 
        container = Container.objects.get(pk=container_pk)
        container.mark_as_empty
        return JsonResponse({'status': 'success'})