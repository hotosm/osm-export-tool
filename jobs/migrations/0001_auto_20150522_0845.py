# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', 'insert_export_formats'),
    ]

    operations = [
        migrations.RenameField(
            model_name='job',
            old_name='the_geom_mercator',
            new_name='the_geom_webmercator',
        ),
    ]
