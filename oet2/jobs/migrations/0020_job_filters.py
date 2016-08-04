# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0019_job_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='filters',
            field=django.contrib.postgres.fields.ArrayField(default=[], base_field=models.CharField(default='', max_length=50, blank=True), size=None),
        ),
    ]
