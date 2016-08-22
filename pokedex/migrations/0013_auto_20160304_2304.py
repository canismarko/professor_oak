# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import pokedex.models


class Migration(migrations.Migration):

    dependencies = [
        ('pokedex', '0012_auto_20160304_1848'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sample',
            name='analysis_EC',
        ),
        migrations.RemoveField(
            model_name='sample',
            name='analysis_TEM',
        ),
        migrations.RemoveField(
            model_name='sample',
            name='analysis_TGA',
        ),
        migrations.RemoveField(
            model_name='sample',
            name='analysis_XAS',
        ),
        migrations.RemoveField(
            model_name='sample',
            name='analysis_XRD',
        ),
        migrations.AddField(
            model_name='sample',
            name='file_photo',
            field=models.FileField(blank=True, upload_to='./pokedex/data/Photo', null=True),
        ),
        migrations.AlterField(
            model_name='sample',
            name='file_EC',
            field=models.FileField(blank=True, upload_to='./pokedex/data/EC', null=True, validators=[pokedex.models.validate_file_extension]),
        ),
        migrations.AlterField(
            model_name='sample',
            name='file_TEM',
            field=models.FileField(blank=True, upload_to='./pokedex/data/TEM', null=True, validators=[pokedex.models.validate_file_extension]),
        ),
        migrations.AlterField(
            model_name='sample',
            name='file_TGA',
            field=models.FileField(blank=True, upload_to='./pokedex/data/TGA', null=True, validators=[pokedex.models.validate_file_extension]),
        ),
        migrations.AlterField(
            model_name='sample',
            name='file_XAS',
            field=models.FileField(blank=True, upload_to='./pokedex/data/XAS', null=True, validators=[pokedex.models.validate_file_extension]),
        ),
        migrations.AlterField(
            model_name='sample',
            name='file_XRD',
            field=models.FileField(blank=True, upload_to='./pokedex/data/XRD', null=True, validators=[pokedex.models.validate_file_extension]),
        ),
    ]
