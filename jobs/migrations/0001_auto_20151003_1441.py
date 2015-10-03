# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', 'install_default_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='key',
            field=models.CharField(default='', max_length=50, db_index=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='value',
            field=models.CharField(default='', max_length=50, db_index=True),
        ),
    ]
