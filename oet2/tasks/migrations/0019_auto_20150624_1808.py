# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0018_auto_20150624_1736'),
    ]

    operations = [
        migrations.AddField(
            model_name='exporttaskresult',
            name='filename',
            field=models.CharField(max_length=100, editable=False, blank=True),
        ),
        migrations.AddField(
            model_name='exporttaskresult',
            name='size',
            field=models.FloatField(null=True, editable=False),
        ),
    ]
