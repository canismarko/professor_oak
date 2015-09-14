# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chemical_inventory', '0002_auto_20150912_0630'),
    ]

    operations = [
        migrations.RenameField(
            model_name='container',
            old_name='empty_status',
            new_name='is_empty',
        ),
    ]
