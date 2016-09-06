# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0014_auto_20150622_1848'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exporttaskresult',
            name='output_url',
        ),
        migrations.AddField(
            model_name='exporttaskresult',
            name='download_url',
            field=models.URLField(default='', verbose_name='Url to export task result output.'),
            preserve_default=False,
        ),
    ]
