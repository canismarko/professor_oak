# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pokedex', '0002_auto_20160225_0101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sample',
            name='experiment_atmosphere',
            field=models.CharField(choices=[('Argon', 'Argon'), ('5%H2:95%N2', '5%H2:95%N2'), ('Oxygen', 'Oxygen'), ('Nitrogen', 'Nitrogen'), ('Air', 'Air')], max_length=50),
        ),
        migrations.AlterField(
            model_name='sample',
            name='experiment_equation',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='sample',
            name='experiment_medium',
            field=models.CharField(choices=[('Ballmill', 'Ballmill'), ('Tube: Borosilicate', 'Tube: Borosilicate'), ('Tube: Quartz', 'Tube: Quartz'), ('Tube: Alumina', 'Tube: Alumina')], max_length=50),
        ),
        migrations.AlterField(
            model_name='sample',
            name='experiment_temperature',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
