# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0004_auto_20150825_1141'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='groups',
            field=django.contrib.postgres.fields.ArrayField(default=[], base_field=models.CharField(default='', max_length=100, blank=True), size=None),
        ),
    ]
