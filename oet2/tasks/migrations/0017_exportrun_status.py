# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0016_auto_20150624_1506'),
    ]

    operations = [
        migrations.AddField(
            model_name='exportrun',
            name='status',
            field=models.CharField(default='', max_length=20, db_index=True, blank=True),
        ),
    ]
