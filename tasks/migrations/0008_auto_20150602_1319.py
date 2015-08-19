# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0007_remove_exportrun_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exportrun',
            name='finished_at',
            field=models.DateTimeField(null=True, editable=False),
        ),
        migrations.AlterField(
            model_name='exporttask',
            name='finished_at',
            field=models.DateTimeField(null=True, editable=False),
        ),
    ]
