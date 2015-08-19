# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from ..models import ExportFormat


class Migration(migrations.Migration):
    
    def insert_export_formats(apps, schema_editor):
        ExportFormat = apps.get_model('jobs', 'ExportFormat')
        ExportFormat.objects.create(name='OBF Format', description='OSMAnd OBF Export Format.',
                                    slug='OBF')
        ExportFormat.objects.create(name='ESRI Shapefile Format', description='ESRI Shapefile Export Format.',
                                    slug='SHP')
        ExportFormat.objects.create(name='KML Format', description='KML Export Format.',
                                    slug='KML')
        ExportFormat.objects.create(name='SQLITE Format', description='SQLITE Export Format.',
                                    slug='SQLITE')
        ExportFormat.objects.create(name='Garmin Map Format', description='Garmin Map Export Format.',
                                    slug='GARMIN')

    dependencies = [
        ('jobs', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(insert_export_formats),
    ]
