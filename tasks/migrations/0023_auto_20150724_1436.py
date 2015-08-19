# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0022_exportrun_created_at'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='exporttask',
            options={'ordering': ['-started_at'], 'managed': True},
        ),
    ]
