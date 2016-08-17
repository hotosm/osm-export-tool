# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from django.db import models, migrations
from django.contrib.auth.models import Group
from oet2.jobs.models import ExportProfile


class Migration(migrations.Migration):

    def insert_default_group(apps, schema_editor):
        """
        Set up the default group and group profile.
        """
        Group = apps.get_model('auth', 'Group')
        ExportProfile = apps.get_model('jobs', 'ExportProfile')
        group = Group.objects.create(name='DefaultExportExtentGroup')
        profile = ExportProfile.objects.create(
            name='DefaultExportProfile',
            max_extent=2500000,
            group=group
        )

    dependencies = [
        ('jobs', 'install_region_mask'),
    ]

    operations = [
        migrations.RunPython(insert_default_group),
    ]
