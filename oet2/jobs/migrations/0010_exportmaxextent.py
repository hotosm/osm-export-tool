# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0009_auto_20150907_1140'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExportMaxExtent',
            fields=[
                ('id', models.AutoField(serialize=False, editable=False, primary_key=True)),
                ('name', models.CharField(default='', max_length=100)),
                ('max_extent', models.IntegerField()),
            ],
        ),
    ]
