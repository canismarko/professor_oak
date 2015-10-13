from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse, NoReverseMatch

from .context_processors import breadcrumbs

class BreadcrumbTest(TestCase):
    def setUp(self):
        self.request = RequestFactory().get(reverse('inventory_main'))

    def test_return_dict(self):
        context = breadcrumbs(self.request)
        self.assertTrue(isinstance(context, dict))

    def test_reverse_url(self):
        """Check that passing just a name will resolve the url."""
        self.request.breadcrumbs = ['inventory_main']
        context = breadcrumbs(self.request)
        bc_list = context['breadcrumbs']
        self.assertEqual(bc_list[0], ('Inventory Main', '/chemical_inventory/'))

    def test_pass_tuple(self):
        """Check that passing a name/url tuple just adds the tuple."""
        self.request.breadcrumbs = [('Chemical Inventory', '/chemical_inventory/')]
        context = breadcrumbs(self.request)
        bc_list = context['breadcrumbs']
        self.assertEqual(bc_list[0], ('Chemical Inventory', '/chemical_inventory/'))

    def test_pass_bad_url_name(self):
        self.request.breadcrumbs = ['gibberish']
        with self.assertRaises(NoReverseMatch):
            breadcrumbs(self.request)
