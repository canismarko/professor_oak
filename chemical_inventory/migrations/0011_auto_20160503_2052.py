# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chemical_inventory', '0010_alter_supporting_document_file'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hazard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hazard_type', models.CharField(choices=[('p', 'Physical'), ('h', 'Health'), ('ph', 'Physical and Health'), ('e', 'Environmental')], max_length=4)),
                ('name', models.CharField(max_length=30)),
                ('description', models.TextField(blank=True)),
                ('pictogram', models.ImageField(null=True, upload_to='ghs_pictograms')),
            ],
        ),
        migrations.AlterModelOptions(
            name='supplier',
            options={'ordering': ['name']},
        ),
        migrations.AddField(
            model_name='chemical',
            name='primary_hazard',
            field=models.ForeignKey(null=True, to='chemical_inventory.Hazard'),
        ),
        migrations.AddField(
            model_name='location',
            name='compatible_hazards',
            field=models.ManyToManyField(to='chemical_inventory.Hazard'),
        ),
    ]
