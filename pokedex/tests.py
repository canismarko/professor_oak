import re, pandas as pd, numpy as np

from . import models, views
from unittest import skip
from django.test import TestCase, override_settings
from django.conf import settings
# class SampleAPITest(TestCase):


@skip
class SampleTest(TestCase):
    """Unit tests for the Sample class"""
    
    def setUp(self):
        self.sample = models.Sample(name='Manganese(III) Oxide')
    
    @override_settings(MEDIA_ROOT='pokedex/fixtures/')
    def test_make_XAS_data(self):
        """Tests that XAS data processing of example files results in a dataframe"""
        test_data = [
            ('JLApr16.0364', 'APS: 4-ID-C', pd.core.frame.DataFrame), # Sample data from 4-ID-C
            ('SigScan.25746', 'ALS: 6.1.2', pd.core.frame.DataFrame), # Sample data from ALS612
            ('SigScan.56038', 'ALS: 8.0.1', pd.core.frame.DataFrame), # Sample data from ALS801
            ('SigScan.56038', 'APS: 4-ID-C', str),  # Valid datafile with the wrong beamline
        ]
        for filename, beamline, exp_out in test_data:
            result = views.SampleDetailView.make_XAS_data(filename=filename, beamline=beamline)
            self.assertEqual(exp_out, type(result)) 
        
    def test_normalize_dataframe(self):
        """Tests that normalization values are between 0 and 1"""
        test_df = pd.DataFrame(data=np.random.randn(100, 1))
        result = views.SampleDetailView.normalize_dataframe(test_df)
        self.assertEqual(1, result[0].max())
        self.assertEqual(0, result[0].min())
