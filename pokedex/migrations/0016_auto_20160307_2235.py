# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pokedex', '0015_auto_20160307_2232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sample',
            name='experiment_atmosphere',
            field=models.CharField(choices=[('Argon', 'Argon'), ('5%H2:95%N2', '5%H2:95%N2'), ('Oxygen', 'Oxygen'), ('Nitrogen', 'Nitrogen'), ('Air', 'Air')], max_length=50),
        ),
    ]
