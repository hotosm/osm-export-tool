# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields.hstore


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0024_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='data_model',
            field=models.CharField(default='', max_length=10, db_index=True),
        ),
        migrations.AddField(
            model_name='tag',
            name='geom_types',
            field=django.contrib.postgres.fields.hstore.HStoreField(default={}),
        ),
    ]
