# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pokedex', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sample',
            options={'ordering': ['sample_number']},
        ),
        migrations.RenameField(
            model_name='sample',
            old_name='sample_id',
            new_name='sample_number',
        ),
    ]
