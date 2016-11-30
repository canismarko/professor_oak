# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chemical_inventory', '0013_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='StandardOperatingProcedure',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('file', models.FileField(upload_to='SOPs')),
                ('associated_chemicals', models.ManyToManyField(blank=True, related_name='sop', to='chemical_inventory.Chemical')),
                ('certified_users', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Standard Operating Procedures (SOPs)',
                'verbose_name': 'Standard Operating Procedure (SOP)',
            },
        ),
        migrations.AlterField(
            model_name='container',
            name='owner',
            field=models.ForeignKey(default=0, to=settings.AUTH_USER_MODEL),
        ),
    ]
