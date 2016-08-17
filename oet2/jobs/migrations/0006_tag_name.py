# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0005_tag_groups'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='name',
            field=models.CharField(default='', max_length=100, db_index=True),
        ),
    ]
