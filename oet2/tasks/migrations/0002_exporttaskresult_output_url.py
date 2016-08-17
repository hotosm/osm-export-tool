# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='exporttaskresult',
            name='output_url',
            field=models.URLField(default='', verbose_name='Url to export task result.'),
            preserve_default=False,
        ),
    ]
