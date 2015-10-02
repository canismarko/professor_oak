import datetime
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


class OldDatabaseTest(TestCase):
    """Tests for importing the old database."""
    fixtures = ['inventory_test_data', 'cabana_users']
    chemicalfile = 'chemical_inventory/old-test-chemicals.csv'
    containerfile = 'chemical_inventory/old-test-containers.csv'
    def setUp(self):
        self.convert_chemicals = models.import_chemicals_csv
        self.convert_containers = models.import_containers_csv
        self.nitrile_glove = models.Glove.objects.get(name='Nitrile')

    def test_convert_chemicals(self):
        # Clear out chemicals loaded by fixture
        models.Chemical.objects.all().delete()
        assert models.Chemical.objects.count() == 0
        # Load new chemicals
        self.convert_chemicals(self.chemicalfile)
        # Check first imported material
        lithium = models.Chemical.objects.first()
        self.assertEqual(lithium.cas_number, '7439-93-2')
        self.assertEqual(lithium.name, 'Lithium')
        self.assertEqual(lithium.formula, 'Li')
        self.assertEqual(lithium.health, 3)
        # Default glove is set?
        self.assertIn(self.nitrile_glove, lithium.gloves.all())
        # Other gloves set
        castor_oil = models.Chemical.objects.get(pk=12)
        assert castor_oil.name == 'Castor Oil'
        latex_glove = models.Glove.objects.get(name='Latex')
        self.assertIn(latex_glove, castor_oil.gloves.all())
        # Test if formula numbers are subscripted
        magnesium_hydroxide = models.Chemical.objects.get(name='Magnesium Hydroxide')
        self.assertEqual(magnesium_hydroxide.formula, 'Mg(OH)_2')

    def test_convert_containers(self):
        # Delete current container list
        models.Container.objects.all().delete()
        self.convert_containers(self.containerfile)
        # Check first imported container
        container = models.Container.objects.first()
        self.assertEqual(container.chemical.name, 'Lithium')
        self.assertEqual(container.expiration_date, datetime.date(2015, 8, 7))
        self.assertEqual(container.chemical.cas_number, '7439-93-2')
        new_location = models.Location.objects.get(name='Glove Box @ 4163')
        self.assertEqual(container.location, new_location)
        self.assertEqual(container.batch, 'SZBE0200V')
        new_supplier = models.Supplier.objects.get(name='Sigma-Aldrich')
        self.assertEqual(container.supplier, new_supplier)
        self.assertEqual(container.state, 'Solid')
        self.assertEqual(container.container_type, 'Glass Bottle')
        self.assertEqual(container.owner.first_name, 'Mike')
        self.assertEqual(container.quantity, 25)
        self.assertEqual(container.unit_of_measure, 'g')
