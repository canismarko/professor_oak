# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('chemical_inventory', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='standardoperatingprocedure',
            options={'verbose_name': 'Standard Operating Procedure (SOP)', 'verbose_name_plural': 'Standard Operating Procedures (SOPs)', 'ordering': ['name']},
        ),
        migrations.AlterField(
            model_name='standardoperatingprocedure',
            name='verified_users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True, related_name='sop'),
        ),
    ]
