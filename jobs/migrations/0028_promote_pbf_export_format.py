# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    def promote_pbf_export_format(apps, schema_editor):
        ExportFormat = apps.get_model('jobs', 'ExportFormat')
        ExportFormat.objects.create(name='PBF Format', description='OSM PBF',
                                    slug='PBF')

    dependencies = [
        ('jobs', '0001_auto_20151003_1441'),
    ]

    operations = [
        migrations.RunPython(promote_pbf_export_format),
    ]
