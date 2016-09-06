# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0002_auto_20150813_0655'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='published',
            field=models.BooleanField(default=False),
        ),
    ]
