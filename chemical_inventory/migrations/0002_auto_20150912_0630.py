# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('chemical_inventory', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chemical',
            name='special_hazards',
            field=models.CharField(choices=[('W', '̶Water reactive (̶W)'), ('OX', 'Oxidizer (OX)'), ('SA', 'Simple asphyxiant (SA)')], max_length=2, blank=True),
        ),
        migrations.AlterField(
            model_name='container',
            name='date_opened',
            field=models.DateField(null=True, default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='container',
            name='emptied_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True, related_name='emptied_containers'),
        ),
        migrations.AlterField(
            model_name='container',
            name='empty_status',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='container',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='container',
            name='unit_of_measure',
            field=models.CharField(null=True, max_length=20, blank=True),
        ),
        migrations.DeleteModel(
            name='LabUser',
        ),
    ]
