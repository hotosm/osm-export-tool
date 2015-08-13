# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0001_auto_20150813_0654'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exportconfig',
            name='published',
            field=models.BooleanField(default=False),
        ),
    ]
