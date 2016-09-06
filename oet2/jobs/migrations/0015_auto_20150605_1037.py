# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0014_exportconfig_content_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='exportconfig',
            name='name',
            field=models.CharField(default='', max_length=255, db_index=True),
        ),
        migrations.AddField(
            model_name='exportconfig',
            name='visible',
            field=models.BooleanField(default=True),
        ),
    ]
