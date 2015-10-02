# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chemical_inventory', '0004_auto_20150925_2317'),
    ]

    operations = [
        migrations.AddField(
            model_name='chemical',
            name='safety_data_sheet',
            field=models.FileField(null=True, upload_to='safety_data_sheets'),
        ),
    ]
