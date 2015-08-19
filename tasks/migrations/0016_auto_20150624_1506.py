# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0015_auto_20150624_1503'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exporttaskresult',
            name='download_url',
            field=models.URLField(max_length=254, verbose_name='Url to export task result output.'),
        ),
    ]
