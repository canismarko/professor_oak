# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pokedex', '0003_auto_20160225_1942'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sample',
            old_name='experiment_temperature',
            new_name='experiment_variable',
        ),
        migrations.AddField(
            model_name='sample',
            name='variable_units',
            field=models.CharField(blank=True, max_length=5),
        ),
    ]
