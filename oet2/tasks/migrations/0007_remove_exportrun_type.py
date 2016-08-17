# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0006_auto_20150602_1312'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exportrun',
            name='type',
        ),
    ]
