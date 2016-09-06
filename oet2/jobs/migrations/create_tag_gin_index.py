# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0027_tag_geom_types'),
    ]

    operations = [
        migrations.RunSQL('CREATE INDEX geom_types_gin_idx ON tags USING gin(geom_types);')
    ]
