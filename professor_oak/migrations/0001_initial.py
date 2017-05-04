# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import professor_oak.models
import django.contrib.auth.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='OakUser',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=(professor_oak.models.ScoreMixin, 'auth.user'),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
