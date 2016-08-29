# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pokedex', '0005_sample_experiment_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='sample',
            name='analysis_EC',
            field=models.BooleanField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sample',
            name='analysis_TEM',
            field=models.BooleanField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sample',
            name='analysis_TGA',
            field=models.BooleanField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sample',
            name='analysis_XAS',
            field=models.BooleanField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sample',
            name='analysis_XRD',
            field=models.BooleanField(default=0),
            preserve_default=False,
        ),
    ]
