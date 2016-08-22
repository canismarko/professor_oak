# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('sample_id', models.CharField(max_length=10, db_index=True)),
                ('name', models.CharField(max_length=200, db_index=True)),
                ('formula', models.CharField(max_length=50, blank=True, db_index=True)),
                ('stripped_formula', models.CharField(max_length=50, blank=True, db_index=True)),
                ('experiment_medium', models.IntegerField(choices=[(0, 'Ballmill'), (1, 'Tube: Borosilicate'), (2, 'Tube: Quartz'), (3, 'Tube: Alumina')])),
                ('experiment_atmosphere', models.IntegerField(choices=[(0, 'Argon'), (1, '5%H2:95%N2'), (2, 'Oxygen'), (3, 'Nitrogen'), (4, 'Air')])),
                ('experiment_temperature', models.FloatField()),
                ('experiment_equation', models.CharField(max_length=200)),
                ('start_date', models.DateField(default=datetime.date.today, null=True)),
                ('end_date', models.DateField(default=datetime.date.today, null=True)),
                ('user', models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['sample_id'],
            },
        ),
    ]
