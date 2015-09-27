# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chemical_inventory', '0003_auto_20150913_1435'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chemical',
            name='glove',
        ),
        migrations.AddField(
            model_name='chemical',
            name='gloves',
            field=models.ManyToManyField(to='chemical_inventory.Glove'),
        ),
        migrations.AlterField(
            model_name='chemical',
            name='special_hazards',
            field=models.CharField(max_length=2, blank=True, choices=[('W', 'Water reactive (W)'), ('OX', 'Oxidizer (OX)'), ('SA', 'Simple asphyxiant (SA)')]),
        ),
    ]
