from django.test import TestCase

from . import models Chemical

# Create your tests here.
class ChemicalTest(TestCase):
    """Unit tests for the Chemical class."""

    def setUp(self):
        self.chemical = Chemical()

    def test_is_in_stock(self):
        self.assertFalse(self.chemical.is_in_stock())
