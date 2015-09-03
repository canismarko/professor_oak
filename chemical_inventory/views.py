from django.shortcuts import render

# Create your views here.
def main(request):
    """This view function returns a generic landing page response."""
    # A 'context' is the data that the template can use
    context = {'inventory_size': 0}
    # Now put the context together with a template
    # Look in chemical_inventory/templates/main.html for the actual html
    # 'request' is the HTTP request submitted by the browser
    return render(request, 'main.html', context)
