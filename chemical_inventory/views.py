from collections import namedtuple
import re
import datetime as dt
import urllib
import warnings

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, FormView
from rest_framework import viewsets, permissions, response, status
from django.utils.safestring import mark_safe
from django.http import HttpResponseRedirect, JsonResponse
from django.conf import settings
from django.db.models import Q, Count, F
from django_subquery.expressions import Subquery, OuterRef, Exists

from .forms import ChemicalForm, ContainerForm, GloveForm, SupplierForm, SupportingDocumentForm
from .models import Chemical, Hazard, Container, Glove, Supplier, SupportingDocument
import xkcd
from .serializers import ChemicalSerializer, HazardSerializer, ContainerSerializer, GloveSerializer, SupplierSerializer
from professor_oak.views import breadcrumb, BreadcrumbsMixin


GLOSSARY_FILTERS = ( '0-9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
	             'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
	             'U', 'V', 'W', 'X', 'Y', 'Z' )

# Breadcrumbs definitions
def inventory_breadcrumb():
    return breadcrumb('Chemical Inventory', reverse_lazy('inventory_main'))

def chemical_breadcrumbs(chemical):
    return [
        inventory_breadcrumb(),
        'chemical_list',
        breadcrumb(
            chemical.name,
            reverse('chemical_detail', kwargs={'pk': chemical.pk})
        )
    ]

def annotate_chemical_queryset(queryset):
    """Take a queryset of chemical objects and add annotations.
    
    Adds the following attributes to each chemical:
    - num_containers
    - has_expired_containers
    - is_in_stock
    
    This is most efficient if the queryset has not yet been evaluated,
    saving a bunch of unnecessary calls.
    
    """
    # Annotations for determining if there are any containers
    queryset = queryset.annotate(num_containers=Count('container'))
    # Annotations for determining if there are expired containers
    expired_containers = Container.objects.filter(
        is_empty=False, chemical=OuterRef('pk'),
        expiration_date__lte=dt.date.today()
    )
    queryset = queryset.annotate(has_expired_containers=Exists(expired_containers))
    # Sort by the number of containers available
    full_containers = Container.objects.filter(is_empty=False, chemical=OuterRef('pk'))
    queryset = queryset.annotate(is_in_stock=Exists(full_containers))
    return queryset


class ElementSearchView(BreadcrumbsMixin, TemplateView):
    template_name = 'element_search.html'
    def breadcrumbs(self):
        breadcrumbs = [
            inventory_breadcrumb(),
            'chemical_list',
            'element_search',
        ]
        return breadcrumbs
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        query_params = self.request.GET
        # Filter required elements
        included_symbols = query_params.getlist('required')
        excluded_symbols = query_params.getlist('excluded')
        context['included_elements'] = included_symbols
        context['excluded_elements'] = excluded_symbols
        chemical_qs = Chemical.objects.all()
        if included_symbols == [] and excluded_symbols == []:
            # No search terms passed
            chemical_qs = Chemical.objects.none()
        else:
            chemical_qs = Chemical.objects.all()
        for symbol in included_symbols:
            regex = r'{symbol}[^a-z]|{symbol}$'.format(symbol=symbol)
            chemical_qs = chemical_qs.filter(formula__regex=regex)
        for symbol in excluded_symbols:
            regex = r'{symbol}[^a-z]|{symbol}$'.format(symbol=symbol)
            chemical_qs = chemical_qs.exclude(formula__regex=regex)
        # Filter excluded elements
        chemical_qs = annotate_chemical_queryset(chemical_qs)
        chemical_qs = chemical_qs.order_by('-is_in_stock')
        context['chemicals'] = chemical_qs
        # Check if an failure message should be displayed
        is_query = (len(included_symbols) > 0 or len(excluded_symbols) >0)
        context['failed_search'] = len(chemical_qs) == 0 and is_query
        return context


class Main(BreadcrumbsMixin, TemplateView):
    template_name = 'main.html'

    def get_context_data(self, xkcd_api=xkcd, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # A 'context' is the data that the template can use
        # Update inventory data
        context.update({
            'inventory_size': Container.objects.filter(is_empty=False).count(),
        })
        # Get the latest XKCD comic to show the user
        try:
            comic = xkcd_api.Comic(xkcd_api.getLatestComicNum())
        except urllib.error.URLError:
            # Problems getting the latest comic (maybe offline?)
            warnings.warn("Could not acquire latest XKCD comic")
            context.update({
                'xkcd_url': '',
                'xkcd_alt': '',
                'xkcd_title': '',
            })        
        else:
            context.update({
                'xkcd_url': comic.getImageLink(),
                'xkcd_alt': comic.getAsciiAltText(),
                'xkcd_title': comic.getAsciiTitle()
            })        
        return context
    
    def breadcrumbs(self):
        breadcrumbs = [inventory_breadcrumb()]
        return breadcrumbs


class ChemicalListView(BreadcrumbsMixin, ListView):
    """View shows a list of currently available chemicals."""
    
    template_name = 'chemical_list.html'
    model = Chemical
    glossary_filters = GLOSSARY_FILTERS
    context_object_name = 'chemicals'
    
    def breadcrumbs(self):
        breadcrumbs = [inventory_breadcrumb()]
        breadcrumbs.append('chemical_list')
        return breadcrumbs
    
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
            query = (Q(formula__icontains=searchstring) |
                     Q(name__icontains=searchstring) |
                     Q(stripped_formula__icontains=searchstring) |
                     Q(cas_number=searchstring))
            queryset = queryset.filter(query)
        # For leading digits
        if filterstring == '0-9':
            queryset = queryset.filter(name__regex=r'^\d').exclude(name__isnull=True)
        # For everything else
        elif filterstring is not None:  #Ignores empty returns
            queryset = queryset.filter(name__istartswith=filterstring).exclude(name__isnull=True)
        queryset = annotate_chemical_queryset(queryset)
        queryset = queryset.order_by('-is_in_stock')
        return queryset


class ChemicalDetailView(BreadcrumbsMixin, DetailView):
    """This view shows detailed information about one chemical. Also gets
    the list of containers that this chemical is in.
    
    """
    template_name = 'chemical_detail.html'
    template_object_name = 'chemical'
    model = Chemical
    
    def breadcrumbs(self):
        return chemical_breadcrumbs(self.object)
    
    def get_context_data(self, *args, **kwargs):
        chemical = self.get_object()
        # Get the default context
        context = super().get_context_data(*args, **kwargs)
        #sets the active find to an integer from ?find= found in the URL
        if self.request.GET.get('find') is not None: #avoids error with empty ?find=
            context['active_find'] = int(self.request.GET.get('find'))
        # Add list of containers to context
        related_fields = ('location', 'owner', 'chemical')
        container_list = chemical.container_set.select_related(*related_fields)
        container_list = container_list.prefetch_related('supportingdocument_set')
        container_list = container_list.order_by('is_empty', 'expiration_date')
        context['container_list'] = container_list
        return context


class SupportingDocumentView(BreadcrumbsMixin, FormView):
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
    
    def breadcrumbs(self):
        # Set breadcrumbs
        breadcrumbs = chemical_breadcrumbs(self.container.chemical)
        breadcrumbs.append(('Supporting Documents',
                            self.get_success_url()))
        return breadcrumbs
    
    def get_context_data(self, *args, **kwargs):
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


def container_detail(request, pk):
    container = Container.objects.get(pk=pk)
    # Redirect this view to the chemical detail with the given container highlighted
    url = reverse('chemical_detail', kwargs={'pk': container.chemical.pk})
    url += "?find={}".format(pk)
    return redirect(url, permanent=True)


class AddContainerView(BreadcrumbsMixin, TemplateView):
    template_name = 'container_add.html'
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # Load the angular forms for container and chemical
        context.update(chemical_form=ChemicalForm())
        context.update(container_form=ContainerForm())
        context.update(glove_form=GloveForm())
        context.update(supplier_form=SupplierForm())
        return context
    
    def breadcrumbs(self):
        # Add breadcrumbs
        chemical_id = self.request.GET.get('chemical_id')
        if chemical_id is not None:
            chemical = Chemical.objects.get(pk=chemical_id)
            breadcrumbs = chemical_breadcrumbs(chemical)
        else:
            breadcrumbs = [inventory_breadcrumb()]
        breadcrumbs.append(('Add to Inventory', reverse('add_container')))
        return breadcrumbs
    
    @property
    def success_url(self):
        # Look up the url for the chemical that this inventory belongs to
        url = reverse('chemical_detail', kwargs={'pk': self.object.chemical.pk})
        return url
    
    @success_url.setter
    def success_url(self, url):
        # Django throws an error if it can't set success_url
        pass


class EditChemicalView(BreadcrumbsMixin, UpdateView):
    template_name = 'chemical_edit.html'
    template_object_name = 'chemical'
    model = Chemical
    form_class = ChemicalForm
    
    def breadcrumbs(self):
        return [
            inventory_breadcrumb(),
            'chemical_list',
            breadcrumb(self.object.name,
                       reverse('chemical_detail', kwargs={'pk': self.object.pk})),
            breadcrumb('Edit',
                       reverse('chemical_edit', kwargs={'pk': self.object.pk})),
            ]


class EditContainerView(BreadcrumbsMixin, UpdateView):
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

    def breadcrumbs(self):
        # Set the breadcrumb navigation
        breadcrumbs = [
            inventory_breadcrumb(),
            'chemical_list',
            breadcrumb(self.object.chemical.name, reverse('chemical_detail', kwargs={'pk': self.object.chemical.pk})),
            breadcrumb('Edit container', reverse('container_edit', kwargs={'pk': self.object.pk})),
            ]
        return breadcrumbs


# class StandardOperatingProceduresListView(BreadcrumbsMixin, ListView):
#     """View shows a list of all Standard Operating Procedures (SOPs)"""

#     template_name = 'all_SOPs.html'
#     model = StandardOperatingProcedures
#     context_object_name = 'sop'

#     def breadcrumbs(self):
#         breadcrumbs = [inventory_breadcrumb()]
#         breadcrumbs.append('sop_list')
#         return breadcrumbs

#     def get_context_data(self, *args, **kwargs):
#         # Get the default context
#         context = super().get_context_data(*args, **kwargs)
#         return context

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


class HazardViewSet(viewsets.ModelViewSet):
    """Viewset for the Chemical model. User is required to be logged in to
    post."""
    # Determine which object to list
    queryset = Hazard.objects.all()
    # Decide how to convert to JSON
    serializer_class = HazardSerializer
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
        print_label = data.pop('$print_label', False);
        # Set the owner to be the request user
        data['owner'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # Print a label
        if print_label:
            container = Container.objects.get(id=serializer.data['id'])
            container.print_label()
        headers = self.get_success_headers(serializer.data)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


@login_required
def print_label(request, container_pk):
    """Pass the information from the container to subprocess, convert it
    to a csv file and merge with the gLabel template.
    """
    container = Container.objects.get(pk=container_pk)
    container.print_label()
    return JsonResponse({'status': 'success'})
