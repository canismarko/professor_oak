# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import professor_oak.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Chemical',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(db_index=True, max_length=200)),
                ('cas_number', models.CharField(db_index=True, blank=True, max_length=100)),
                ('formula', models.CharField(db_index=True, blank=True, max_length=50)),
                ('stripped_formula', models.CharField(db_index=True, blank=True, max_length=50)),
                ('health', models.IntegerField(choices=[(0, 'None (0)'), (1, 'Low (1)'), (2, 'Caution (2)'), (3, 'Warning (3)'), (4, 'Danger (4)')])),
                ('flammability', models.IntegerField(choices=[(0, 'None (0)'), (1, 'Low (1)'), (2, 'Caution (2)'), (3, 'Warning (3)'), (4, 'Danger (4)')])),
                ('instability', models.IntegerField(choices=[(0, 'None (0)'), (1, 'Low (1)'), (2, 'Caution (2)'), (3, 'Warning (3)'), (4, 'Danger (4)')])),
                ('special_hazards', models.CharField(blank=True, choices=[('W', 'Water reactive (W)'), ('OX', 'Oxidizer (OX)'), ('SA', 'Simple asphyxiant (SA)')], max_length=2)),
                ('safety_data_sheet', models.FileField(null=True, blank=True, upload_to='safety_data_sheets')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Container',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('batch', models.CharField(blank=True, max_length=30)),
                ('date_added', models.DateTimeField(auto_now=True)),
                ('date_opened', models.DateField(null=True, default=datetime.date.today)),
                ('expiration_date', models.DateField()),
                ('state', models.CharField(max_length=10)),
                ('container_type', models.CharField(max_length=50)),
                ('quantity', models.FloatField(null=True, blank=True)),
                ('unit_of_measure', models.CharField(null=True, blank=True, max_length=20)),
                ('is_empty', models.BooleanField(default=False)),
                ('barcode', models.CharField(blank=True, max_length=30)),
                ('comment', models.TextField(blank=True)),
                ('chemical', models.ForeignKey(to='chemical_inventory.Chemical')),
                ('emptied_by', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, related_name='emptied_containers', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Glove',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Hazard',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('hazard_type', models.CharField(choices=[('p', 'Physical'), ('h', 'Health'), ('ph', 'Physical and Health'), ('e', 'Environmental')], max_length=4)),
                ('name', models.CharField(max_length=30)),
                ('description', models.TextField(blank=True)),
                ('pictogram', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(blank=True, max_length=50)),
                ('room_number', models.CharField(max_length=20)),
                ('building', models.CharField(max_length=30)),
                ('msds_location', models.CharField(blank=True, max_length=60)),
                ('compatible_hazards', models.ManyToManyField(to='chemical_inventory.Hazard')),
            ],
            bases=(professor_oak.models.ScoreMixin, models.Model),
        ),
        migrations.CreateModel(
            name='StandardOperatingProcedure',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('file', models.FileField(upload_to='SOPs')),
                ('associated_chemicals', models.ManyToManyField(related_name='sop', to='chemical_inventory.Chemical', blank=True)),
                ('verified_users', models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'verbose_name_plural': 'Standard Operating Procedures (SOPs)',
                'verbose_name': 'Standard Operating Procedure (SOP)',
            },
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='SupportingDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('file', models.FileField(upload_to='supporting_documents')),
                ('comment', models.TextField(blank=True)),
                ('date_added', models.DateTimeField(auto_now=True)),
                ('container', models.ForeignKey(to='chemical_inventory.Container')),
                ('owner', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='glove',
            name='supplier',
            field=models.ManyToManyField(to='chemical_inventory.Supplier', blank=True),
        ),
        migrations.AddField(
            model_name='container',
            name='location',
            field=models.ForeignKey(to='chemical_inventory.Location'),
        ),
        migrations.AddField(
            model_name='container',
            name='owner',
            field=models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='container',
            name='supplier',
            field=models.ForeignKey(null=True, to='chemical_inventory.Supplier', blank=True),
        ),
        migrations.AddField(
            model_name='chemical',
            name='ghs_hazards',
            field=models.ManyToManyField(to='chemical_inventory.Hazard', blank=True),
        ),
        migrations.AddField(
            model_name='chemical',
            name='gloves',
            field=models.ManyToManyField(to='chemical_inventory.Glove'),
        ),
    ]
