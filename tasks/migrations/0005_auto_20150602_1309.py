# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0004_auto_20150601_1122'),
    ]

    operations = [
        migrations.AddField(
            model_name='exporttask',
            name='status',
            field=models.CharField(db_index=True, max_length=20, blank=True),
        ),
        migrations.AlterField(
            model_name='exportrun',
            name='finished_at',
            field=models.DateTimeField(editable=False),
        ),
        migrations.AlterField(
            model_name='exportrun',
            name='job',
            field=models.ForeignKey(related_name='runs', to='jobs.Job'),
        ),
        migrations.AlterField(
            model_name='exporttask',
            name='finished_at',
            field=models.DateTimeField(editable=False),
        ),
        migrations.AlterField(
            model_name='exporttaskresult',
            name='task',
            field=models.OneToOneField(related_name='result', primary_key=True, serialize=False, to='tasks.ExportTask'),
        ),
    ]
