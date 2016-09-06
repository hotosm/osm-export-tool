# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0013_auto_20150603_1223'),
    ]

    operations = [
        migrations.AddField(
            model_name='exportconfig',
            name='content_type',
            field=models.CharField(default='text/plain', max_length=30, editable=False),
            preserve_default=False,
        ),
    ]
