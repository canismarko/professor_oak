# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pokedex', '0007_auto_20160227_1920'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user_project',
            options={'verbose_name_plural': 'User Projects', 'verbose_name': 'User Project'},
        ),
    ]
