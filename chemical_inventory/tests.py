import json

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User

from . import models

# Create your tests here.
class ChemicalTest(TestCase):
    """Unit tests for the Chemical class."""

    def setUp(self):
        self.chemical = models.Chemical()

    def test_is_in_stock(self):
        self.assertFalse(self.chemical.is_in_stock())

class ContainerAPITest(TestCase):
    fixtures = ['cabana_users.json', 'inventory_test_data.json']
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
