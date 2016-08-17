# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0003_job_region'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='region',
            field=models.ForeignKey(to='jobs.Region', null=True),
        ),
    ]
