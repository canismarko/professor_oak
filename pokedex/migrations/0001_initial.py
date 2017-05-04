# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('sample_number', models.CharField(db_index=True, max_length=10)),
                ('name', models.CharField(db_index=True, max_length=200)),
                ('formula', models.CharField(blank=True, db_index=True, max_length=50)),
                ('stripped_formula', models.CharField(blank=True, db_index=True, max_length=50)),
                ('file_XAS', models.FileField(blank=True, upload_to='./pokedex/data/XAS', null=True)),
                ('beamline', models.CharField(max_length=50)),
                ('date_created', models.DateField(default=datetime.date.today, null=True)),
                ('edge', models.CharField(max_length=2)),
                ('comment', models.TextField(blank=True)),
                ('user', models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
