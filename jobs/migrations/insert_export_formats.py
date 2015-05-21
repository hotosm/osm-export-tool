# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from ..models import ExportFormat


class Migration(migrations.Migration):
    
    def insert_export_formats(apps, schema_editor):
        ExportFormat = apps.get_model('jobs', 'ExportFormat')
        ExportFormat.objects.create(name='OBF Format', description='OSMAnd OBF Export Format.',
                                    code='OBF')
        ExportFormat.objects.create(name='ESRI Shapefile Format', description='ESRI Shapefile Export Format.',
                                    code='SHP')

    dependencies = [
        ('jobs', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(insert_export_formats)
    ]
