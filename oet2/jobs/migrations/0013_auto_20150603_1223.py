# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0012_auto_20150603_1212'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exportconfig',
            name='description',
        ),
        migrations.RemoveField(
            model_name='exportconfig',
            name='name',
        ),
    ]
