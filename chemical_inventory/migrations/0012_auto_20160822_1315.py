# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chemical_inventory', '0011_auto_20160503_2052'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hazard',
            name='pictogram',
            field=models.ImageField(blank=True, null=True, upload_to='ghs_pictograms'),
        ),
    ]
