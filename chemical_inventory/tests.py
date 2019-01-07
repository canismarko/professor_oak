from unittest import skip, skipIf, expectedFailure
import datetime
import json
import os
import time
import re

from django.db.models import QuerySet
from django.conf import settings
from django.test import TestCase, RequestFactory, Client
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from rest_framework.test import APIRequestFactory, APIClient

from . import models, serializers, views

HAS_CHEMSPIDER_KEY = hasattr(settings, 'CHEMSPIDER_KEY')

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


class InventoryViewTest(TestCase):
    fixtures = ['test_users', 'inventory_test_data']
    
    def setUp(self):
        self.factory = RequestFactory()
    
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
        self.assertEqual(len(qs), 4)
    
    def test_chemical_list_as_view(self):
        list_view = views.ChemicalListView.as_view()
        request = self.factory.get(reverse('chemical_list'))
        response = list_view(request)
        # Check that the database is not hit too much
        self.assertEqual(response.status_code, 200)
    
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
    
    @skipIf(HAS_CHEMSPIDER_KEY, 'CHEMSPIDER_KEY found in localsettings.py')
    def test_chemspider_url_without_key(self):
        target_url = 'http://discovermagazine.com/~/media/Images/Zen%20Photo/N/nanoputian/3487.gif'
        structure_url = self.chemical.structure_url()
        self.assertEqual(structure_url, target_url)
        
    @skipIf(not HAS_CHEMSPIDER_KEY, 'CHEMSPIDER_KEY not found in localsettings.py')
    def test_chemspider_url_with_key(self):
        target_url = 'https://www.chemspider.com/'
        structure_url = self.chemical.structure_url()
        self.assertNotIn('discovermagazine.com', structure_url,
                         'Default URL found. Check settings.CHEMSPIDER_KEY')
        self.assertEqual(structure_url[:len(target_url)],target_url)


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


class IsEmptyTest(TestCase):
    '''Test for verifying whether a chemical as an expired but non-empty
    container'''
    fixtures = ['inventory_test_data','test_users']
    def test_not_empty_expired(TestCase):
        for chemicals in models.Chemical.objects.all():
            container_test = models.Container.objects.filter(
                chemical__id=chemicals.pk,
                expiration_date__lte=datetime.date.today(),
                is_empty=False).count()
            # print (container_test)
            assert type(container_test) is int




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

    def test_edit_url(self):
        self.assertEqual(self.container.edit_url(), '/chemical_inventory/containers/edit/26/')

    def test_detail_url(self):
        self.assertEqual(self.container.detail_url(), '/chemical_inventory/chemicals/1/')

    def test_is_expired(self):
        self.assertEqual(self.container.is_expired(), True)

    def test_get_absolute_url(self):
        self.assertEqual(self.container.get_absolute_url(), '/chemical_inventory/chemicals/1/')

    def test_mark_as_empty(self):
        self.container.mark_as_empty()
        self.assertEqual(self.container.is_empty, True)

        # Now check the value from the database
        db_container = models.Container.objects.get(pk=self.container.pk)
        self.assertEqual(db_container.is_empty, True) 

    def test_quantity_string(self):
        self.assertEqual(self.container.quantity_string(), '75.0 g')



