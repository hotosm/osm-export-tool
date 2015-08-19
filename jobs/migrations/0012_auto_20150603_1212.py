# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0011_auto_20150603_1030'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exportconfig',
            name='config_type',
            field=models.CharField(default='PRESET', max_length=11, choices=[('PRESET', 'Preset'), ('TRANSLATION', 'Translation'), ('TRANSFORM', 'Transform')]),
        ),
    ]
