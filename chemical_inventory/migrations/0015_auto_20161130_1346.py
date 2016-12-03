# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('chemical_inventory', '0014_mike_old_migrations'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chemical',
            name='primary_hazard',
        ),
        migrations.AddField(
            model_name='chemical',
            name='ghs_hazards',
            field=models.ManyToManyField(to='chemical_inventory.Hazard'),
        ),
        migrations.AlterField(
            model_name='container',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='hazard',
            name='pictogram',
            field=models.TextField(null=True, blank=True),
        ),
    ]
