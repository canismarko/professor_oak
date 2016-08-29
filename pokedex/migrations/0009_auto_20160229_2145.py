# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pokedex', '0008_auto_20160229_2143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sample',
            name='experiment_time',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
