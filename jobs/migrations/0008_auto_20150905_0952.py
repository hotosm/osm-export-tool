# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0007_auto_20150828_1317'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='event',
            field=models.CharField(default='', max_length=100, db_index=True, blank=True),
        ),
    ]
