# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import image_cropping.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pokedex', '0013_auto_20160304_2304'),
    ]

    operations = [
        migrations.AddField(
            model_name='sample',
            name='cropping',
            field=image_cropping.fields.ImageRatioField('file_photo', '300x300', verbose_name='cropping', free_crop=False, hide_image_field=False, adapt_rotation=False, size_warning=False, allow_fullsize=False, help_text=None),
        ),
        migrations.AlterField(
            model_name='sample',
            name='file_photo',
            field=models.ImageField(blank=True, upload_to='./pokedex/data/Photo', null=True),
        ),
    ]
