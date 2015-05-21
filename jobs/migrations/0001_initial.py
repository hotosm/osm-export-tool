# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.utils.timezone
import jobs.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ExportFormat',
            fields=[
                ('id', models.AutoField(serialize=False, editable=False, primary_key=True)),
                ('uid', models.UUIDField(default=uuid.uuid4, unique=True, editable=False)),
                ('name', models.CharField(max_length=100)),
                ('slug', jobs.models.LowerCaseCharField(default='', unique=True, max_length=7)),
                ('description', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
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
                ('id', models.AutoField(serialize=False, editable=False, primary_key=True)),
                ('uid', models.UUIDField(blank=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(serialize=False, editable=False, primary_key=True)),
                ('uid', models.UUIDField(default=uuid.uuid4, unique=True, editable=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=65000)),
                ('status', models.CharField(max_length=30)),
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
