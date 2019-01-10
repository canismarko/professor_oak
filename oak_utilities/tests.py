import io

from django.test import TestCase, RequestFactory
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile, UploadedFile

from . import models
from .views import UploadInventoryView
from .forms import UploadInventoryForm, validate_stock_take

# Create your tests here.


class StockTakeViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
    
    def test_context_data(self):
        view = UploadInventoryView()
        context = view.get_context_data()
        self.assertIn('stock_takes', context.keys())


class StockTakeFormTest(TestCase):
    def setUp(self):
        self.stock_take = models.stock_take()
        self.factory = RequestFactory()
    
    def test_init(self):
        form = UploadInventoryForm(instance=self.stock_take)

    def test_clean(self):
        data = {
            'file': None
        }
        form = UploadInventoryForm(data)
        self.assertFalse(form.is_valid())
        # Now try a valid form
        good_file = SimpleUploadedFile('stock-take.txt', b'0012\n0013\n\n')
        file_dict = {'file': good_file}
        form = UploadInventoryForm({}, file_dict)
        self.assertTrue(form.is_valid())
    
    def test_stock_take_is_valid(self):
        lines = (b'001\n', b'002\r\n', b'', b'%%15\r\n')
        valid, invalid = validate_stock_take(lines)
        self.assertEqual(valid, [1 ,2])
        self.assertEqual(invalid, ['%%15'])
