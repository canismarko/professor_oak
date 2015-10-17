# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chemical_inventory', '0008_chemical_stripped_formula'),
    ]

    operations = [
        migrations.CreateModel(
            name='SupportingDocument',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=50)),
                ('file', models.FileField(upload_to='')),
                ('comment', models.TextField(blank=True)),
                ('date_added', models.DateTimeField(auto_now=True)),
                ('container', models.ForeignKey(to='chemical_inventory.Container')),
                ('owner', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, blank=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='safetydatasheet',
            name='chemical',
        ),
        migrations.RemoveField(
            model_name='safetydatasheet',
            name='supplier',
        ),
        migrations.DeleteModel(
            name='SafetyDataSheet',
        ),
    ]
