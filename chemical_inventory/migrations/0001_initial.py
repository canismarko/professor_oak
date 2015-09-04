# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chemical',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('cas_number', models.CharField(db_index=True, blank=True, max_length=10)),
                ('name', models.CharField(max_length=200)),
                ('formula', models.CharField(blank=True, max_length=50)),
                ('health', models.IntegerField(choices=[(0, 'None (0)'), (1, 'Low (1)'), (2, 'Caution (2)'), (3, 'Warning (3)'), (4, 'Danger (4)')])),
                ('flammability', models.IntegerField(choices=[(0, 'None (0)'), (1, 'Low (1)'), (2, 'Caution (2)'), (3, 'Warning (3)'), (4, 'Danger (4)')])),
                ('instability', models.IntegerField(choices=[(0, 'None (0)'), (1, 'Low (1)'), (2, 'Caution (2)'), (3, 'Warning (3)'), (4, 'Danger (4)')])),
                ('special_hazards', models.CharField(choices=[('W', '̶Water reactive (̶W'), ('OX', 'Oxidizer (OX)'), ('SA', 'Simple asphyxiant (SA)')], blank=True, max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='Container',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('batch', models.CharField(blank=True, max_length=30)),
                ('date_added', models.DateTimeField(auto_now=True)),
                ('date_opened', models.DateField(null=True)),
                ('expiration_date', models.DateField()),
                ('state', models.CharField(max_length=10)),
                ('container_type', models.CharField(max_length=50)),
                ('quantity', models.FloatField(blank=True, null=True)),
                ('unit_of_measure', models.CharField(null=True, max_length=20)),
                ('empty_status', models.BooleanField()),
                ('barcode', models.CharField(blank=True, max_length=30)),
                ('chemical', models.ForeignKey(to='chemical_inventory.Chemical')),
            ],
        ),
        migrations.CreateModel(
            name='Glove',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='LabUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('room_number', models.CharField(max_length=20)),
                ('building', models.CharField(max_length=30)),
                ('name', models.CharField(blank=True, max_length=50)),
                ('msds_location', models.CharField(blank=True, max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name='SafetyDataSheet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('sds_file', models.FileField(upload_to='')),
                ('chemical', models.ForeignKey(to='chemical_inventory.Chemical')),
            ],
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='safetydatasheet',
            name='supplier',
            field=models.ForeignKey(to='chemical_inventory.Supplier'),
        ),
        migrations.AddField(
            model_name='glove',
            name='supplier',
            field=models.ManyToManyField(blank=True, to='chemical_inventory.Supplier'),
        ),
        migrations.AddField(
            model_name='container',
            name='emptied_by',
            field=models.ForeignKey(blank=True, null=True, related_name='emptied_containers', to='chemical_inventory.LabUser'),
        ),
        migrations.AddField(
            model_name='container',
            name='location',
            field=models.ForeignKey(to='chemical_inventory.Location'),
        ),
        migrations.AddField(
            model_name='container',
            name='owner',
            field=models.ForeignKey(to='chemical_inventory.LabUser'),
        ),
        migrations.AddField(
            model_name='container',
            name='supplier',
            field=models.ForeignKey(blank=True, null=True, to='chemical_inventory.Supplier'),
        ),
        migrations.AddField(
            model_name='chemical',
            name='glove',
            field=models.ForeignKey(to='chemical_inventory.Glove'),
        ),
    ]
