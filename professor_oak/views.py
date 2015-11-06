"""Views for main professor_module. Most views will belong to a
specific app. This module is mostly for default/landing pages."""

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render
from django.views.generic.detail import DetailView

from chemical_inventory.models import expired_containers

class UserView(DetailView):
    model = User
    template_name = 'user_detail.html'
    context_object_name = 'target_user'

    # @login_required
    # def dispatch(self, *args, **kwargs):
    #     return super().dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        containers = self.object.container_set.all()
        context['container_list'] = containers.order_by('chemical', 'is_empty', 'expiration_date')
        # Compile chemical inventory statistics for this user
        stats = {
            'expired_containers': expired_containers().filter(owner=self.object).count(),
            'total_containers': self.object.container_set.count()
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
