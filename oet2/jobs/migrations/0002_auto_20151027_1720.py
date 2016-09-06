# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0001_auto_20151003_1441'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='jobs.Region', null=True),
        ),
    ]
