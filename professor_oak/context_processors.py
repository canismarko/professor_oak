import random
from collections import namedtuple

from django.core.urlresolvers import reverse, NoReverseMatch

def skynet(request):
    """Show some humorous message related to Terminator movies."""
    jake_emails = [
        # 'mark.wolf.music@gmail.com',
        # 'plews2@uic.edu',
        'lapping1@uic.edu',
    ]
    is_jake = (not request.user.is_anonymous()) and (request.user.email in jake_emails)
    saving_throw = random.randrange(0, 20)
    skynet = (is_jake and not saving_throw)
    return {'skynet': skynet}

breadcrumb = namedtuple('breadcrumb', ('name', 'url'))

def breadcrumbs(request):
    """Return a list of names and links that the user can follow for
    navigation. Can be either a 2-tuple of (name, url) or a string to be
    reversed"""
    trail = getattr(request, 'breadcrumbs', [])
    new_trail = []
    for step in trail:
        try:
            new_trail.append(breadcrumb(*step))
        except TypeError:
            # Reverse the urls if possible
            url = reverse(step)
            name = step.replace('_', ' ').title()
            new_trail.append(breadcrumb(name, url))
    return {
        'breadcrumbs': new_trail
    }
