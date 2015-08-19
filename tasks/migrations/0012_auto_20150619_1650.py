# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0011_auto_20150602_1914'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exporttaskexception',
            name='exception',
            field=models.TextField(editable=False),
        ),
    ]
