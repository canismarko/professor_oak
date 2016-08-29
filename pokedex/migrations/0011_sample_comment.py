# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pokedex', '0010_auto_20160229_2146'),
    ]

    operations = [
        migrations.AddField(
            model_name='sample',
            name='comment',
            field=models.TextField(blank=True),
        ),
    ]
