# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from ..models import ExportFormat


class Migration(migrations.Migration):

    def promote_osm_export_format(apps, schema_editor):
        ExportFormat = apps.get_model('jobs', 'ExportFormat')
        ExportFormat.objects.create(name='OSM XML Format', description='OSM XML',
                                    slug='OSM')

    dependencies = [
        ('jobs', '0003_auto_20151027_1807'),
    ]

    operations = [
        migrations.RunPython(promote_osm_export_format),
    ]
