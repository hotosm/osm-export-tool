# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0017_exportrun_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exporttask',
            name='started_at',
            field=models.DateTimeField(null=True, editable=False),
        ),
    ]
