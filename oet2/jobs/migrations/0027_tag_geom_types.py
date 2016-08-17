# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0026_remove_tag_geom_types'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='geom_types',
            field=django.contrib.postgres.fields.ArrayField(default=[], base_field=models.CharField(default='', max_length=10, blank=True), size=None),
        ),
    ]
