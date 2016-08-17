# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_exporttaskresult_output_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='exportrun',
            name='run_type',
            field=models.CharField(default='EXPORT', max_length=6, editable=False, db_index=True),
        ),
    ]
