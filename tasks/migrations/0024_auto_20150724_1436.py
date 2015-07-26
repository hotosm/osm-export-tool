# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0023_auto_20150724_1436'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='exporttask',
            options={'ordering': ['started_at'], 'managed': True},
        ),
    ]
