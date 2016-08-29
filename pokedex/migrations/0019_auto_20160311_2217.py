# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import image_cropping.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pokedex', '0018_auto_20160311_2214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sample',
            name='file_photo',
            field=image_cropping.fields.ImageCropField(blank=True, null=True, upload_to='./pokedex/data/Photo'),
        ),
    ]
