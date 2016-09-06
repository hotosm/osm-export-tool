# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0007_exportconfig'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='exportconfig',
            options={'managed': True},
        ),
        migrations.AlterModelTable(
            name='exportconfig',
            table='export_configurations',
        ),
    ]
