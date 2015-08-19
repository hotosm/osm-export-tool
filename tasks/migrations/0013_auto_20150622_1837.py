# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0012_auto_20150619_1650'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exporttask',
            name='uid',
            field=models.UUIDField(null=True),
        ),
    ]
