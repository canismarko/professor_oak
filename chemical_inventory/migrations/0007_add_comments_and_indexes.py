# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chemical_inventory', '0006_auto_20151002_1449'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chemical',
            options={'ordering': ['name']},
        ),
        migrations.AddField(
            model_name='container',
            name='comment',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='chemical',
            name='formula',
            field=models.CharField(max_length=50, db_index=True, blank=True),
        ),
        migrations.AlterField(
            model_name='chemical',
            name='name',
            field=models.CharField(max_length=200, db_index=True),
        ),
    ]
