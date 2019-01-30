from unittest import skip, skipIf, expectedFailure, mock
import datetime
import json
import os
import time
import re
import urllib
import warnings

from django.db.models import QuerySet
from django.conf import settings
from django.test import TestCase, RequestFactory, Client
from django.http import HttpResponse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIRequestFactory, APIClient

from . import models, serializers, views, reports
from .templatetags.custom_filters import formula_markup, subtract

HAS_CHEMSPIDER_KEY = hasattr(settings, 'CHEMSPIDER_KEY')


class MainViewTest(TestCase):
    """Check that the landing view works properly."""
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
    
    def test_as_view(self):
        view = views.Main.as_view()
        request = self.factory.get(reverse('inventory_main'))
        response = view(request)
        self.assertEqual(response.status_code, 200)
    
    def test_get_context_data(self):
        view = views.Main()
        # Prepare a fake xkcd api
        xkcd_api = mock.MagicMock()
        context = view.get_context_data(xkcd_api=xkcd_api)
        # Check for the inventory size
        count = models.Container.objects.filter(is_empty=False).count()
        self.assertEqual(context['inventory_size'], count)
        # Check that the XKCD comic is present
        self.assertIn('xkcd_url', context.keys())
        self.assertIn('xkcd_alt', context.keys())
        self.assertIn('xkcd_title', context.keys())
    
    def test_bad_xkcd(self):
        view = views.Main()
        # Prepare an XKCD api that raises a url exception
        xkcd_api = mock.MagicMock()
        xkcd_api.getLatestComicNum.side_effect = urllib.error.URLError('Testing')
        # Call the actual view
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore',
                                    message='Could not acquire latest XKCD comic')
            context = view.get_context_data(xkcd_api=xkcd_api)
        # Check that blank values are returned for the latest comic 
        self.assertEqual(context['xkcd_url'], '')
    
    def test_client(self):
        response = self.client.get(reverse('inventory_main'))
        self.assertEqual(response.status_code, 200)


class EditContainerViewTest(TestCase):
    fixtures = ['test_users.json', 'inventory_test_data']
    def setUp(self):
        self.factory = RequestFactory()


class AddContainerViewTest(TestCase):
    fixtures = ['test_users.json']
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
    
    def test_as_view(self):
        view = views.AddContainerView.as_view()
        request = self.factory.get(reverse('add_container'))
        response = view(request)
        self.assertEqual(response.status_code, 200)
    
    def test_with_client(self):
        # Check without logging in (it should redirect to login)
        response = self.client.get(reverse('add_container'))
        self.assertEqual(response.status_code, 302)
        login_url = reverse('login_page') + '?next=' + reverse('add_container')
        self.assertIn(login_url, response.url)
        # Now log in and check again
        self.client.login(username='test', password='secret')
        response = self.client.get(reverse('add_container'))
        self.assertEqual(response.status_code, 200)


class ContainerDetailViewTest(TestCase):
    fixtures = ['test_users', 'inventory_test_data']
    def setUp(self):
        self.factory = RequestFactory()
    
    def test_redirect(self):
        pk = 14
        container = models.Container.objects.get(pk=pk)
        request = self.factory.get(reverse('container_detail', kwargs={'pk': pk}))
        response = views.container_detail(request, pk=pk)
        # Check that the view redirects to its parent chemical
        self.assertEqual(response.status_code, 301)
        new_url = reverse('chemical_detail', kwargs={'pk': container.chemical.pk})
        new_url += '?find={}'.format(container.pk)
        self.assertEqual(response.url, new_url)


class SupportingDocumentViewTest(TestCase):
    fixtures = ['test_users', 'inventory_test_data']
    def setUp(self):
        self.client = Client()
    
    def test_with_client(self):
        container_pk = 14
        url = reverse('supporting_documents', kwargs={'container_pk': container_pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class ElementSearchTest(TestCase):
    """Filtering a list of chemicals by symbols in the formula."""
    fixtures = ['test_users.json', 'inventory_test_data.json']
    def test_included_elements(self):
        c = Client()
        response = c.get(
            reverse('element_search'),
            {'required':['Li']}
        )
        chemicals = response.context['chemicals']
        lithium = models.Chemical.objects.get(formula='Li')
        self.assertEqual(len(chemicals), 1)
        self.assertEqual(chemicals[0], lithium)
    
    def test_excluded_elements(self):
        c = Client()
        response = c.get(
            reverse('element_search'),
            {'excluded':['Li']}
        )
        chemicals = response.context['chemicals']
        self.assertFalse("Li" in [c.formula for c in chemicals])
    
    def test_no_elements(self):
        c = Client()
        response = c.get(reverse('element_search'))
        chemicals = response.context['chemicals']
        self.assertEqual(len(chemicals), 0)
    
    def test_two_letter_elements(self):
        """Make sure eg. searching H doesn't return He."""
        c = Client()
        response = c.get(
            reverse('element_search'),
            {'required':['H']}
        )
        chemicals = response.context['chemicals']
        self.assertTrue(len(chemicals) > 0)
        self.assertFalse('He' in [chemical.formula for chemical in chemicals])


class ChemicalAPITest(TestCase):
    fixtures = ['test_users.json', 'inventory_test_data.json']

    def test_many_to_many(self):
        test_data = {
            'name': "Francium",
            'health': '1',
            'flammability': '1',
            'instability': '1',
            'gloves': ['1','2'],
        }
        url = reverse('api:chemical-list')
        client = APIClient()
        client.login(username="test", password="secret")
        response = client.post(url, test_data)
        self.assertEqual(response.status_code, 201)
        # request = APIRequestFactory().post(url, test_data)
        # chemical_view = views.ChemicalViewSet().as_view()
        # chemical_view(request)


class ChemicalListViewTest(TestCase):
    fixtures = ['test_users', 'inventory_test_data']
    
    def setUp(self):
        self.factory = RequestFactory()
    
    def test_search_list(self):
        view = views.ChemicalListView.as_view()
        # Do a basic search string_instance
        request = self.factory.get(reverse('chemical_list'), {'search':'lithium'})
        response = view(request)
        context = response.context_data
        self.assertEqual(context['active_search'], 'lithium')
        # Check that it found the one and only lithium
        self.assertEqual(len(context['object_list']), 1)
        self.assertEqual(context['object_list'][0],
                         models.Chemical.objects.get(name='Lithium'))
    
    def test_filter_list(self):
        view = views.ChemicalListView.as_view()
        # Filter by alphabetical value
        request = self.factory.get(reverse('chemical_list'), {'filter': 'L'})
        response = view(request)
        context = response.context_data
        self.assertEqual(context['active_filter'], 'L')
        # Check that if found things starting with lithium
        self.assertEqual(len(context['object_list']), 1)
        self.assertEqual(context['object_list'][0],
                         models.Chemical.objects.get(name='Lithium'))
        # Filter by 0-9 value
        request = self.factory.get(reverse('chemical_list'), {'filter': '0-9'})
        response = view(request)
        context = response.context_data
        self.assertEqual(context['active_filter'], '0-9')
        # Check that if found things starting with numbers
        self.assertEqual(len(context['object_list']), 1)
        self.assertEqual(context['object_list'][0],
                         models.Chemical.objects.get(name='2-propanol'))
    
    def test_annotate_chemical_queryset(self):
        qs = models.Chemical.objects.all()
        new_qs = views.annotate_chemical_queryset(qs)
        # Make sure the querysets have the same items
        self.assertEqual(len(qs), len(new_qs))
        self.assertEqual([q.pk for q in qs], [q.pk for q in new_qs],
                         'QuerySet modified during annotation')
        # Check that stock-level annotations are set
        for chemical in new_qs:
            num_containers = chemical.container_set.count()
            self.assertEqual(chemical.num_containers, num_containers)
            num_empty = chemical.container_set.filter(is_empty=True).count()
            has_stock = (num_containers - num_empty) > 0
            self.assertEqual(chemical.is_in_stock, has_stock)
            has_expired_containers = chemical.container_set.filter(
                expiration_date__lte=datetime.date.today(),
                is_empty=False).exists()
            self.assertEqual(chemical.has_expired_containers, has_expired_containers)
    
    def test_chemical_list_queryset(self):
        list_view = views.ChemicalListView()
        list_view.request = self.factory.get(reverse('chemical_list'))
        # Retrieve the queryset
        qs = list_view.get_queryset()
        self.assertIsInstance(qs, QuerySet)
        # Check that the database is not hit too much
        with self.assertNumQueries(1):
            list(qs)
            [q.is_in_stock for q in qs]
            [q.num_containers for q in qs]
            [q.has_expired_containers for q in qs]
        self.assertEqual(len(qs), models.Chemical.objects.count())
    
    def test_chemical_list_as_view(self):
        list_view = views.ChemicalListView.as_view()
        request = self.factory.get(reverse('chemical_list'))
        response = list_view(request)
        # Check that the database is not hit too much
        self.assertEqual(response.status_code, 200)


class ChemicalDetailViewTest(TestCase):
    fixtures = ['test_users', 'inventory_test_data']
    def setUp(self):
        self.factory = RequestFactory()
    
    def test_chemical_detail_as_view(self):
        list_view = views.ChemicalDetailView.as_view()
        request = self.factory.get(reverse('chemical_list'))
        request.user = User.objects.get(username='test')
        with self.assertNumQueries(7):
            response = list_view(request, pk=1)
            response.render()
        # Check that the database is not hit too much
        self.assertEqual(response.status_code, 200)


class ChemicalTest(TestCase):
    """Unit tests for the Chemical class."""
    # fixtures=['test_users', 'inventory_test_data']
    
    def setUp(self):
        self.chemical = models.Chemical(name='Acetone')
    
    def test_chemspider_url_without_key(self):
        target_url = 'http://discovermagazine.com/~/media/Images/Zen%20Photo/N/nanoputian/3487.gif'
        structure_url = self.chemical.structure_url(database_api=None)
        self.assertEqual(structure_url, target_url)

    def test_chemspider_url_with_key(self):
        mock_api = mock.MagicMock()
        structure_url = self.chemical.structure_url(database_api=mock_api)
        self.assertNotIn('discovermagazine.com', structure_url,
                         'Default URL found. Make new settings.CHEMSPIDER_KEY from '
                         'https://developer.rsc.org/user/me/apps')
        mock_api.simple_search.assert_called_with(self.chemical.name)


class ContainerAPITest(TestCase):
    fixtures = ['test_users.json', 'inventory_test_data.json']
    def setUp(self):
        # Create a dummy user
        self.user = User.objects.create_user('john',
                                             'john.lennon@example.com',
                                             'secret')
        self.client.login(username='john', password='secret')
    
    def test_auto_owner(self):
        """Make sure that creating a new chemical automatically sets the owner."""
        response = self.client.post(
            '/chemical_inventory/api/containers/',
            {'chemical': 1,
             'location': 1,
             'container_type': 'glass',
             'expiration_date': '2015-01-01',
             'state': 'powder'},
        )
        data = json.loads(response.content.decode())
        # Verify the object was created
        self.assertEqual(
            response.status_code,
            201
        )
        # Verify that `owner` was set
        savedContainer = models.Container.objects.get(pk=data['id'])
        self.assertEqual(
            savedContainer.owner,
            self.user
        )

    def test_iso_datestrings(self):
        """Javascript passes all dates with a time component. Does the
        serializer properly strip this time part."""
        # Make sure it only fixes it if the field is changed
        response = self.client.post(
            '/chemical_inventory/api/containers/',
            {'is_empty': True}
        )
        response = self.client.post(
            '/chemical_inventory/api/containers/',
            {'date_opened': '2015-09-21T19:39:41Z',
             'expiration_date': '2015-09-21T19:39:41Z'}
        )
        # List of errors should not contain anything for date_opened
        self.assertNotContains(response, 'date_opened', status_code=400)
        self.assertNotContains(response, 'expiration_date', status_code=400)


class SearchFormulaTest(TestCase):

    def test_autosave(TestCase):
        """Tests for saving data before strip"""
        chemical = models.Chemical(formula='CoF_2', health='0',
                                   flammability='0', instability='0',
                                   name='Cobalt(II) Fluoride')
        chemical.save()
        cobalt = models.Chemical.objects.get(formula='CoF_2')
        assert cobalt.stripped_formula == 'CoF2'


class ContainerTest(TestCase):
    fixtures = ['test_users.json', 'inventory_test_data.json']
    def setUp(self):
        self.container = models.Container.objects.get(pk=26)
        self.location = models.Location.objects.get(pk=1) 
        self.supplier = models.Supplier.objects.get(pk=1)
        self.chemical = models.Chemical.objects.get(pk=1)       

    def test_setUp(self):
        self.assertEqual(self.container.chemical.name, 'Lithium')
        self.assertEqual(self.container.location.name, 'Glovebox')
        self.assertEqual(self.container.batch, '98567')
        self.assertEqual(self.container.state, 'foil')
        self.assertEqual(self.container.container_type, 'Pouch')
        self.assertEqual(self.container.quantity, 75.0)
        self.assertEqual(self.container.unit_of_measure, 'g')
        self.assertEqual(self.supplier.name, 'Sigma-Aldrich')

    def test__str__(self):
        string_instance=isinstance(self.container.__str__(),str)
        self.assertEqual(self.container.__str__(), 'Lithium (Li) Pouch in Glovebox (4130 SES)')
        self.assertEqual(string_instance, True)

    def test_is_expired(self):
        self.assertEqual(self.container.is_expired(), True)

    def test_quantity_string(self):
        self.assertEqual(self.container.quantity_string(), '75.0 g')


class HazardTest(TestCase):
    fixtures = ['test_users.json', 'inventory_test_data.json']

    def setUp(self):
        self.hazard = models.Hazard(name='Acetone')

    def test__str__(self):
        self.assertEqual(self.hazard.__str__(),'Acetone') 


class GloveTest(TestCase):
    fixtures = ['test_users.json', 'inventory_test_data.json']
    def setUp(self):
        self.glove = models.Glove.objects.get(pk=1)

    def test__str__(self):
        self.assertEqual(str(self.glove),'Nitrile')

class Location(TestCase):
    fixtures = ['test_users.json', 'inventory_test_data.json']
    def setUp(self):
        self.location = models.Location.objects.get(pk=1)
        self.container = models.Container.objects.get(pk=26)
    
    def test_activate_container_set(self):
        self.location.active_container_set


class TemplateTagTest(TestCase):
    def test_formula_markup(self):
        # Formula with no content
        result = formula_markup('')
        self.assertEqual(result, '')
        # Formula with subscript
        result = formula_markup('CH_4')
        self.assertEqual(result, 'CH<sub>4</sub>')
        # Formula with superscript
        result = formula_markup('Li^+')
        self.assertEqual(result, 'Li<sup>+</sup>')
        # Formula with bullet
        result = formula_markup('Mn|3H_2O')
        self.assertEqual(result, 'Mn&bull;3H<sub>2</sub>O')
    
    def test_subtract(self):
        self.assertEqual(subtract(3, 1), 2)


class ReportsTest(TestCase):
    fixtures = ['test_users', 'inventory_test_data']
    
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
    
    def test_container_csv_row(self):
        container = models.Container.objects.get(pk=14)
        row = reports.container_csv_row(container)
        # Check that the result matches what is expected
        expected = (
            container.id,
            container.chemical.name,
            container.batch,
            container.location,
            container.quantity,
            container.unit_of_measure,
            container.expiration_date,
            container.state,
            container.container_type,
            container.owner.get_full_name(),
        )
        self.assertEqual(row, expected)
    
    def test_report_list(self):
        request = self.factory.get(reverse('reports'))
        view = reports.ReportsList.as_view()
        response = view(request)
    
    def test_report_view(self):
        request = self.factory.get(reverse('all_chemicals'))
        view = reports.ReportView()
        view.url_name = None
        # Check that get_queryset is not implemented for the base class
        with self.assertRaises(NotImplementedError):
            response = view.get_queryset()
        # Check that write_csv is not initially set
        with self.assertRaises(NotImplementedError):
            view.write_csv()
        # Check that having no url_name still returns breadcrumbs
        view.breadcrumbs()
    
    def test_report_view_csv(self):
        request = self.factory.get(reverse('all_chemicals'), {'format': 'csv'})
        view = reports.ReportView()
        view.write_csv = mock.MagicMock()
        view.url_name = 'test-file'
        # Check that the response has a csv attachment
        response = view.get(request)
        self.assertEqual(response['Content-Disposition'],
                         'attachment; filename="test-file.csv"')
    
    def test_all_chemicals_as_view(self):
        request = self.factory.get('all_chemicals')
        # Test as a view function
        view = reports.AllChemicals.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
    
    def test_all_chemicals_as_csv(self):
        request = self.factory.get('all_chemicals', {'format': 'csv'})
        # Test as a view function
        view = reports.AllChemicals.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
    
    def test_containers_report(self):
        request = self.factory.get('expired_containers')
        view = reports.ContainersReport()
        response = HttpResponse()
        with self.assertRaises(NotImplementedError):
            view.write_csv(response)
    
    def test_expired_containers(self):
        view = reports.ExpiredContainers.as_view()
        # Test as a view function
        request = self.factory.get(reverse('expired_containers'))
        response = view(request)
        self.assertEqual(response.status_code, 200)
        # Test for csv functionality
        request = self.factory.get(reverse('expired_containers'),
                                   {'format': 'csv'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
    
    def test_active_containers(self):
        view = reports.ActiveContainers.as_view()
        # Test as a view function
        request = self.factory.get(reverse('active_containers'))
        response = view(request)
        self.assertEqual(response.status_code, 200)
        # Test for csv functionality
        request = self.factory.get(reverse('active_containers'),
                                   {'format': 'csv'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
    
    def test_containers_by_location(self):
        view = reports.ContainersByLocation.as_view()
        # Get the regular HTTP view
        request = self.factory.get(reverse('containers_by_location'))
        response = view(request)
        # Get the csv view
        request = self.factory.get(reverse('containers_by_location'),
                                   {'format': 'csv'})
        response = view(request)
    
    def test_containers_by_owner(self):
        view = reports.ContainersByOwner.as_view()
        # Get the regular HTTP view
        request = self.factory.get(reverse('containers_by_owner'))
        response = view(request)
        # Get the csv view
        request = self.factory.get(reverse('containers_by_owner'),
                                   {'format': 'csv'})
        response = view(request)
    
    def test_standard_operating_procedure(self):
        view = reports.StandardOperatingProcedure.as_view()
        # Get the regular HTTP view
        request = self.factory.get(reverse('sop'))
        response = view(request)

class SupplierTest(TestCase):
    fixtures = ['test_users.json', 'inventory_test_data.json']
    def setUp(self):
        self.supplier = models.Supplier.objects.get(pk=1)
    def test__str__(self):
        self.assertEqual(str(self.supplier),'Sigma-Aldrich')

class StandardOperatingProcedureTest(TestCase):
    fixtures = ['test_users.json', 'inventory_test_data.json']
    def setUp(self):
        self.user = User.objects.create_user('john',
                                             'john.lennon@example.com',
                                             'secret')
        self.chemical = models.Chemical.objects.get(pk=1)
        self.file = SimpleUploadedFile('Alkali metal Procedures.pdf', b'Them Procedures Tho!')
        self.sop = models.StandardOperatingProcedure(name = 'Alkali metal Procedures', file = self.file)
        self.sop.save()
    
    def test__str__(self):
        # First try it with no users
        self.assertEqual(str(self.sop),
                         'Alkali metal Procedures (0 verified users)')
        # Now try it with one user
        self.sop.verified_users.add(User.objects.get(pk=1))
        self.assertEqual(str(self.sop),
                         'Alkali metal Procedures (1 verified user)')
        # Now try it with two users
        self.sop.verified_users.add(User.objects.get(pk=2))
        self.assertEqual(str(self.sop),
                         'Alkali metal Procedures (2 verified users)')

class SupportingDocument(TestCase):
    fixtures = ['test_users.json', 'inventory_test_data.json']
    def setUp(self):
        self.user = User.objects.create_user('john',
                                             'john.lennon@example.com',
                                             'secret')
        self.chemical = models.Chemical.objects.get(pk=1)
        self.file = SimpleUploadedFile('Alkali metal Procedures.pdf', b'Them Procedures Tho!')
        self.container = models.Container.objects.get(pk=26)

        self.supdocs = models.SupportingDocument(name = 'lithium-msds', file = self.file, 
        container = self.container)

    def test__str__(self):
        self.assertEqual(str(self.supdocs),'lithium-msds (Lithium (Li): 26)')

class ExpiredContainersTest(TestCase):
    fixtures = ['test_users.json', 'inventory_test_data.json']

    def test_expired_containers(self):
        date = datetime.date.today()
        real_qs = models.Container.objects.filter(expiration_date__lte=date,
                                        is_empty=False)
        def_qs = models.expired_containers()
        self.assertEqual(list(def_qs), list(real_qs))





