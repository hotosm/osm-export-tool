# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('jobs', '0010_exportmaxextent'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default='', max_length=100)),
                ('max_extent', models.IntegerField()),
                ('group', models.OneToOneField(related_name='group_profile', to='auth.Group')),
            ],
            options={
                'db_table': 'group_max_extents',
                'managed': True,
            },
        ),
        migrations.DeleteModel(
            name='ExportMaxExtent',
        ),
    ]
