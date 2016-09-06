# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('jobs', '0011_auto_20150908_1225'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExportProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default='', max_length=100)),
                ('max_extent', models.IntegerField()),
                ('group', models.OneToOneField(related_name='export_profile', to='auth.Group')),
            ],
            options={
                'db_table': 'export_profiles',
                'managed': True,
            },
        ),
        migrations.RemoveField(
            model_name='groupprofile',
            name='group',
        ),
        migrations.DeleteModel(
            name='GroupProfile',
        ),
    ]
