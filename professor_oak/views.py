"""Views for main professor_module. Most views will belong to a
specific app. This module is mostly for default/landing pages."""

from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render

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
