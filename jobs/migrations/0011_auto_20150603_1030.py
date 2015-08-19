# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0010_auto_20150603_0945'),
    ]

    operations = [
        migrations.RenameField(
            model_name='exportconfig',
            old_name='type',
            new_name='config_type',
        ),
    ]
