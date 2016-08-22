# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pokedex', '0017_auto_20160311_1914'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sample',
            name='file_photo',
            field=models.ImageField(upload_to='./pokedex/data/Photo', blank=True, null=True),
        ),
    ]
