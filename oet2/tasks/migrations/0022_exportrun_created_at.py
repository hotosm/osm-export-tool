# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0021_remove_exportrun_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='exportrun',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False),
        ),
    ]
