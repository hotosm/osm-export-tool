# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0008_auto_20150603_0938'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='configs',
            field=models.ManyToManyField(related_name='configs', to='jobs.ExportConfig'),
        ),
    ]
