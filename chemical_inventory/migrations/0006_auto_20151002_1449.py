# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chemical_inventory', '0005_chemical_safety_data_sheet'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chemical',
            name='cas_number',
            field=models.CharField(blank=True, db_index=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='chemical',
            name='safety_data_sheet',
            field=models.FileField(upload_to='safety_data_sheets', blank=True, null=True),
        ),
    ]
