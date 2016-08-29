# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pokedex', '0014_auto_20160307_2110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sample',
            name='experiment_atmosphere',
            field=models.CharField(max_length=50, choices=[('Argon', 'Argon'), ('5%H_2:95%N_2', '5%H2:95%N2'), ('Oxygen', 'Oxygen'), ('Nitrogen', 'Nitrogen'), ('Air', 'Air')]),
        ),
    ]
