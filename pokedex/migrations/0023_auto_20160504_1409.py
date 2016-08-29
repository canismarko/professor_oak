# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pokedex', '0022_auto_20160328_1835'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='is_archived',
            field=models.BooleanField(verbose_name='Archived?', default=False),
        ),
    ]
