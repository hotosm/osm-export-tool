# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', 'create_tag_gin_index'),
    ]

    operations = [
        migrations.RenameField(
            model_name='exportconfig',
            old_name='visible',
            new_name='published',
        ),
    ]
