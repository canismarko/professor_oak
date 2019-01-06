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
    
    @expectedFailure
    def test_chemical_list(self):
        list_view = views.ChemicalListView()
        list_view.request = self.factory.get(reverse('chemical_list'))
        # Check that the database is not hit too much
        with self.assertNumQueries(1):
            qs = list_view.get_queryset()
            list(qs)
        # Check that the num_open_containers annotation is set
        water = qs[0]
        # self.assertIsInstance(qs, QuerySet)
        self.assertEqual(len(qs), 4)


class ChemicalTest(TestCase):
    """Unit tests for the Chemical class."""
    # fixtures=['test_users', 'inventory_test_data']
    
    def setUp(self):
        self.chemical = models.Chemical(name='Acetone')
    
    def test_is_in_stock(self):
        self.assertFalse(self.chemical.is_in_stock())
    
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
