# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0002_auto_20151027_1720'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='configs',
            field=models.ManyToManyField(related_name='configs', to='jobs.ExportConfig', blank=True),
        ),
    ]
