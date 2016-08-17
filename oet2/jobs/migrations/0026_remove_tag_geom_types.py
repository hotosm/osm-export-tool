# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0025_auto_20150731_1033'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tag',
            name='geom_types',
        ),
    ]
