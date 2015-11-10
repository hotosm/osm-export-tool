# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def insert_mwm_formats(apps, schema_editor):
	ExportFormat = apps.get_model('jobs', 'ExportFormat')
  	ExportFormat.objects.create(name='MWM Format', description='Maps.me Format',
  							slug='MWM')

class Migration(migrations.Migration):

	dependencies = [
        ('jobs', '0001_auto_20151003_1441'),
    ]

    	operations = [ 
  		migrations.RunPython(insert_mwm_formats)
    ]
