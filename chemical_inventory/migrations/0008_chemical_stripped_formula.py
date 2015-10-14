# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chemical_inventory', '0007_add_comments_and_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='chemical',
            name='stripped_formula',
            field=models.CharField(db_index=True, blank=True, max_length=50),
        ),
    ]
