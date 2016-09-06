# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0020_job_filters'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='job',
            name='filters',
        ),
    ]
