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
from django.conf import settings
from django.db.models import Q

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

    def _fetch_avail_keyword_glossary_filters(glossary_filters, other_filters={}):
        """
        Processes the glossary filters and checks for available records.
        :param glossary_filters: Tuple.
        :param other_filters: Dict.
        """
        # If not filters passed, bail out gracefully.
        if not glossary_filters:
            return {}
        filters = []
        for filter in glossary_filters:
            avail = False
            if filter is '#':
                # Here we do some special handling of our non-alpha filter.
                # We're using Django's exclude in combination with __regex to find all 
                # rows that start with a number or other non-alpha character.
                results = Keyword.objects.exclude(keyword__regex=r'^[a-zA-Z]')
            else:
                # For regular alpha characters filter with a case insensitive __istartswith
                results = Keyword.objects.filter(keyword__istartswith=filter)

            if other_filters:
                for filter_name, filter_info in other_filters.items():
                    tmp = ''
                    if filter_name is 'Search':
                        # Special handling for a keyword search field since it looks across multiple fields. 
                        tmp = 'results = results.filter('
                        query = []
                        for field in filter_info['fields']:
                            query.append('Q(%s="%s")' % (field, filter_info['value']))
                        tmp += ' | '.join(query)
                        tmp += ')'
                    else:
                        # For all other filters that are not a keyword search, apply them ad a field value pair.
                        if 'field' in info and 'value' in info:
                            tmp = 'results = results.filter(%s="%s")' % (filter_info['field'],filter_info['value'])

                    # Generally I am not a fan of doing exec's in any language, so make sure you've 
                    # done your validation thoroughly when you accepted your GET or POST variables. 
                    if tmp:
                        exec (tmp)
 
            if results:
            # If results were found from the final query, set this filters avail flag to True.
                avail = True
 
            # Add this filter with it's availability flag to the dict that will be returned.
            filters.append({
                'value': filter,
                'display': filter,
                'avail': avail,
            })
 
        return filters
        
    def keywords_page(request):
        """
        Keywords page
        :param request:
        :return keywords page:
        """
        variables = {
            'page_title': 'Keywords',
            'domains': Url.objects.values('domain').distinct().order_by('domain'),  # I'm pulling in possible domain values from a Url model.
            'sort_opts': SORT_OPTS_KEYWORDS,    # This is another global in my settings.py
        }
     
        # The main query. If no options or filters are set, this is all it needs.
        keyword_list = Keyword.objects.all()
     
        set_filters = {}
     
        # Check for the domain filter.
        if 'domain' in request.GET:
            for domain in variables['domains']:
                # Only set the domain filter that was passed if it was already found in the DB.
                if domain['domain'] == request.GET['domain']:
                    # Filter our list.
                    keyword_list = keyword_list.filter(urls__domain=domain['domain']).distinct()
                    # Add this to our filters list that the glossary filter will use to check for available filters.
                    set_filters['Domain'] = {
                        'field': 'urls__domain',
                        'value': domain['domain'],
                    }
     
        # Check for search filter.
        if 'search' in request.GET:
            # Do some scrubbing of the user input string.
            variables['search_string'] = escape(strip_tags(request.GET['search']))
            search_string = strip_tags(request.GET['search'])
            # We want to check for results that match the keyword itself, and also a many-to-many relationship's title. 
            # Make sure you add the .distinct() or you'll likely wind up with duplicates.
            keyword_list = keyword_list.filter(Q(keyword__icontains=search_string) | Q(urls__title__icontains=search_string)).distinct()
            # Add this to our filters list that the glossary filter will use to check for available filters.
            set_filters['Search'] = {
                'fields': ['keyword__icontains', 'urls__title__icontains'],   # Using a list here since we have multiple fields.
                'value': search_string,
            }
     
        # Here is where we make sure the list of filters in the glossary are available for the template.
        variables['glossary_filters'] = _fetch_avail_keyword_glossary_filters(GLOSSARY_FILTERS, set_filters)
     
        # Check for glossary filter and apply it if set.
        if 'glossary' in request.GET:
            # Only apply a filter if we already know about it in the list of possible filters.
            for glossary in variables['glossary_filters']:
                if glossary['value'] == request.GET['glossary']:
                    # Make note of which glossary filter is active so we can style it differently in the template.
                    glossary['active'] = True
                    variables['active_glossary'] = glossary['value']
                    if glossary['value'] is '#':
                        # Here we do some special handling of our non-alpha filter.
                        # We're using Django's exclude in combination with __regex to find all 
                        # rows that start with a number or other non-alpha character.
                        keyword_list = keyword_list.exclude(keyword__regex=r'^[a-zA-Z]')
                    else:
                        # For regular alpha characters filter with a case insensitive __istartswith
                        keyword_list = keyword_list.filter(keyword__istartswith=glossary['value'])
                    set_filters['Glossary'] = {
                        'value': glossary['value'],
                    }
     
        # Check for sort.    
        if 'sort' in request.GET:
            # Only apply the sort if we knew about it in the list of possible sorts.
            for sort in variables['sort_opts']:
                if sort['field'] == request.GET['sort']:
                    sort['default'] = True    # Flag as the default for templating.
                    if sort['dir'] == 'DESC':
                        keyword_list = keyword_list.order_by(sort['field']).reverse()
                    else:
                        keyword_list = keyword_list.order_by(sort['field'])
                else:
                    sort['default'] = False
        else:
            keyword_list = keyword_list.order_by('keyword')   # Our default sort (could use a global setting)
     
     
        # Check on the currently selected number of results to show per page.
        cur_num_show = 0
        # Only use the number to show if it is a digit and in our list of possible values defined in a global.
        if 'show' in request.GET and request.GET['show'].isdigit():
            for opt in NUM_SHOW_OPTS:
                if int(opt['value']) == int(request.GET['show']):
                    cur_num_show = int(request.GET['show'])
     
        if cur_num_show == 0:
            for opt in NUM_SHOW_OPTS:
                if 'default' in opt and opt['default']:
                    cur_num_show = int(opt['value'])
     
        variables['num_show_opts'] = NUM_SHOW_OPTS
        for opt in variables['num_show_opts']:
            if int(opt['value']) == int(cur_num_show):
                opt['default'] = True
            else:
                opt['default'] = False
     
        # Let's use the Django Paginator
        paginator = Paginator(keyword_list, cur_num_show)
     
        # Check for the current page, default to 1.
        cur_page = 1
        if 'page' in request.GET and request.GET['page'].isdigit():
            cur_page = int(request.GET['page'])
     
        keywords = {}
        try:
            keywords = paginator.page(cur_page)
        except PageNotAnInteger:
            keywords = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            keywords = paginator.page(paginator.num_pages)
     
        variables['keywords'] = keywords
     
        return render_to_response(
            'keywords.html',
            variables,
            context_instance=RequestContext(request)
    )
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
