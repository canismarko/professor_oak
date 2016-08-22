# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pokedex', '0004_auto_20160225_1956'),
    ]

    operations = [
        migrations.AddField(
            model_name='sample',
            name='experiment_time',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
