# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0020_auto_20150724_1413'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exportrun',
            name='created_at',
        ),
    ]
