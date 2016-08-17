# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0019_auto_20150624_1808'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='exporttask',
            options={'ordering': ['started_at'], 'managed': True},
        ),
        migrations.AddField(
            model_name='exportrun',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False),
        ),
    ]
