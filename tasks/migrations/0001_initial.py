# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExportRun',
            fields=[
                ('started_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('finished_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('id', models.AutoField(serialize=False, editable=False, primary_key=True)),
                ('uid', models.UUIDField(default=uuid.uuid4, unique=True, editable=False)),
                ('type', models.CharField(max_length=20, db_index=True)),
                ('job', models.ForeignKey(related_name='job', to='jobs.Job')),
            ],
            options={
                'db_table': 'export_runs',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ExportTask',
            fields=[
                ('started_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('finished_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('id', models.AutoField(serialize=False, editable=False, primary_key=True)),
                ('uid', models.UUIDField(blank=True)),
            ],
            options={
                'db_table': 'export_tasks',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ExportTaskResult',
            fields=[
                ('task', models.OneToOneField(primary_key=True, serialize=False, to='tasks.ExportTask')),
            ],
            options={
                'db_table': 'export_task_results',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='exporttask',
            name='run',
            field=models.ForeignKey(related_name='run', to='tasks.ExportRun'),
        ),
    ]
