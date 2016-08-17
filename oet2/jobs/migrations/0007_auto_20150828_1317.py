# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0006_tag_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='feature_pub',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='job',
            name='feature_save',
            field=models.BooleanField(default=False),
        ),
    ]
