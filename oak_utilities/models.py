from django.db import models
from datetime import datetime, date
import os

root_file_storage = 'oak_utilities/chemical_inventory_data/'

def update_filename(instance, filename):
	format = 'stock_take-' + str(date.today()) + '.txt'
	return os.path.join(root_file_storage, format)

class stock_take(models.Model):
    """.csv or .txt file that containes, in a single list, barcode numbers corresponding to id's of containers'"""
    name = models.DateTimeField(default=datetime.now)
    file = models.FileField(upload_to=update_filename)

    def __str__(self):
        return self.name
