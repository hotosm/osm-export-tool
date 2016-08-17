# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0017_auto_20150616_1544'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tag',
            options={'managed': True},
        ),
        migrations.AlterModelTable(
            name='tag',
            table='tags',
        ),
    ]
