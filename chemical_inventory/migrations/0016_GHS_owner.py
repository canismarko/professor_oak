# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('chemical_inventory', '0015_auto_20161130_1346'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chemical',
            name='ghs_hazards',
            field=models.ManyToManyField(blank=True, to='chemical_inventory.Hazard'),
        ),
        migrations.AlterField(
            model_name='container',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
