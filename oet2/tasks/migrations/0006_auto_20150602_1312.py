# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0005_auto_20150602_1309'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exportrun',
            name='finished_at',
            field=models.DateTimeField(editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='exporttask',
            name='finished_at',
            field=models.DateTimeField(editable=False, blank=True),
        ),
    ]
