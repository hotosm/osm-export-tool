# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_exportrun_run_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exportrun',
            name='run_type',
        ),
        migrations.AlterField(
            model_name='exporttask',
            name='run',
            field=models.ForeignKey(related_name='tasks', to='tasks.ExportRun'),
        ),
    ]
