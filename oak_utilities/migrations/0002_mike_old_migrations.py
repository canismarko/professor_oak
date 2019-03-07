# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import oak_utilities.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('oak_utilities', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ULON',
            fields=[
                ('ul', models.AutoField(serialize=False, primary_key=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='ULONs')),
                ('title', models.CharField(max_length=100, blank=True)),
                ('user', models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name_plural': 'ULONs',
                'verbose_name': 'ULON',
            },
        ),
        migrations.AlterModelOptions(
            name='stock_take',
            options={'verbose_name_plural': 'Stock Takes', 'verbose_name': 'Stock Take'},
        ),
        migrations.AlterField(
            model_name='stock_take',
            name='file',
            field=models.FileField(upload_to=oak_utilities.models.update_filename),
        ),
    ]
