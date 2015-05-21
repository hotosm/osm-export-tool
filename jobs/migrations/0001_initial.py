# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields
import django.utils.timezone
import jobs.models
from django.conf import settings
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ExportFormat',
            fields=[
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('id', models.AutoField(serialize=False, editable=False, primary_key=True)),
                ('uid', models.UUIDField(default=uuid.uuid4, unique=True, editable=False)),
                ('name', models.CharField(max_length=100)),
                ('slug', jobs.models.LowerCaseCharField(default='', unique=True, max_length=7)),
                ('description', models.CharField(max_length=255)),
                ('cmd', models.TextField(max_length=1000)),
            ],
            options={
                'db_table': 'export_formats',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ExportTask',
            fields=[
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('id', models.AutoField(serialize=False, editable=False, primary_key=True)),
                ('uid', models.UUIDField(blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('id', models.AutoField(serialize=False, editable=False, primary_key=True)),
                ('uid', models.UUIDField(default=uuid.uuid4, unique=True, editable=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=1000)),
                ('status', models.CharField(max_length=30)),
                ('the_geom', django.contrib.gis.db.models.fields.PolygonField(default='', srid=4326, verbose_name='Extent for export')),
                ('the_geom_mercator', django.contrib.gis.db.models.fields.PolygonField(default='', srid=3857, verbose_name='Mercator extent for export')),
                ('the_geog', django.contrib.gis.db.models.fields.PolygonField(default='', srid=4326, verbose_name='Geographic extent for export', geography=True)),
                ('formats', models.ManyToManyField(related_name='formats', to='jobs.ExportFormat')),
                ('user', models.ForeignKey(related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'jobs',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='exporttask',
            name='job',
            field=models.ForeignKey(related_name='job', to='jobs.Job'),
        ),
    ]
