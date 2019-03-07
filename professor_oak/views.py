"""Views for main professor_module. Most views will belong to a
specific app. This module is mostly for default/landing pages."""

from collections import namedtuple

from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render
from django.views.generic.detail import DetailView

from chemical_inventory.models import expired_containers
from professor_oak.models import OakUser

breadcrumb = namedtuple('breadcrumb', ('name', 'url'))


class BreadcrumbsMixin():
    """Provides context information to allow the template to render a
    breadcrumb navigation trail.
    """
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        try:
            trail = self.breadcrumbs()
        except AttributeError as e:
            trail = []
            raise
        new_trail = []
        for step in trail:
            try:
                new_trail.append(breadcrumb(*step))
            except TypeError:
                # Reverse the urls if possible
                url = reverse_lazy(step)
                name = step.replace('_', ' ').title()
                new_trail.append(breadcrumb(name, url))
        context['breadcrumbs'] = new_trail
        return context
    
    def breadcrumbs(self):
        msg = "Please override the 'breadcrumbs()' method of {}"
        raise NotImplementedError(msg.format(self.__class__))


class UserView(DetailView):
    model = OakUser
    template_name = 'user_detail.html'
    context_object_name = 'target_user'
    
    def get_context_data(self, *args, **kwargs):
        user = self.object
        context = super().get_context_data(*args, **kwargs)
        containers = self.object.container_set.all()
        context['container_list'] = containers.order_by('chemical', 'is_empty', 'expiration_date')
        # Compile chemical inventory statistics for this user
        stats = {
            'expired_containers': expired_containers().filter(owner=self.object).count(),
            'total_containers': user.container_set.count(),
        }
        context['stats'] = stats
        return context

def home(request):
    """This view function returns a generic landing page response."""
    # A template is html with special tags for inserting data
    template = loader.get_template('home.html')
    # A 'context' is the data that the template can use
    context = RequestContext(request, {'user_full_name': 'Mr. Noodle'})
    # Now put the two together into a full HTTP response
    return HttpResponse(template.render(context))

def unauthorized(request):
    """A user has tried to authorize but failed, maybe not in the database."""
    context = {}
    return render(request, 'unauthorized.html', context)
