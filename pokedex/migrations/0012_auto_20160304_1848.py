# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pokedex', '0011_sample_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='sample',
            name='file_EC',
            field=models.FileField(null=True, blank=True, upload_to='EC'),
        ),
        migrations.AddField(
            model_name='sample',
            name='file_TEM',
            field=models.FileField(null=True, blank=True, upload_to='TEM'),
        ),
        migrations.AddField(
            model_name='sample',
            name='file_TGA',
            field=models.FileField(null=True, blank=True, upload_to='TGA'),
        ),
        migrations.AddField(
            model_name='sample',
            name='file_XAS',
            field=models.FileField(null=True, blank=True, upload_to='XRD'),
        ),
        migrations.AddField(
            model_name='sample',
            name='file_XRD',
            field=models.FileField(null=True, blank=True, upload_to='XRD'),
        ),
    ]
