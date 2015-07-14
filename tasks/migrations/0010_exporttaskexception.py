# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0009_exporttask_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExportTaskException',
            fields=[
                ('id', models.AutoField(serialize=False, editable=False, primary_key=True)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('exception', models.CharField(max_length=1000, editable=False)),
                ('task', models.ForeignKey(related_name='exceptions', to='tasks.ExportTask')),
            ],
            options={
                'db_table': 'export_task_exceptions',
                'managed': True,
            },
        ),
    ]
