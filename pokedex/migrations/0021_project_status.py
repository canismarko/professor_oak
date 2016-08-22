# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pokedex', '0020_auto_20160327_0337'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='status',
            field=models.CharField(choices=[('Active', 'Active'), ('Archived', 'Archived')], default=1, max_length=10),
            preserve_default=False,
        ),
    ]
