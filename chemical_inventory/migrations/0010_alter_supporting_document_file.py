# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chemical_inventory', '0009_add_supporting_document'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supportingdocument',
            name='file',
            field=models.FileField(upload_to='supporting_documents'),
        ),
    ]
