# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0010_exporttaskexception'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exporttaskexception',
            name='exception',
            field=models.CharField(max_length=5000, editable=False),
        ),
    ]
