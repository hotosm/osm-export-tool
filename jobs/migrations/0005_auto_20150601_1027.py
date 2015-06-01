# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0004_auto_20150526_1523'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegionMask',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('the_geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326, verbose_name='Mask for export regions')),
            ],
            options={
                'db_table': 'region_mask',
                'managed': False,
            },
        ),
        migrations.RemoveField(
            model_name='exporttask',
            name='job',
        ),
        migrations.DeleteModel(
            name='ExportTask',
        ),
    ]
