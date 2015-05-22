# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jobs.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0001_auto_20150522_0845'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exportformat',
            name='slug',
            field=jobs.models.LowerCaseCharField(default='', unique=True, max_length=7, db_index=True),
        ),
        migrations.AlterField(
            model_name='exportformat',
            name='uid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='uid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True),
        ),
    ]
