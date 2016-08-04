# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0013_auto_20150622_1837'),
    ]

    operations = [
        migrations.AddField(
            model_name='exporttask',
            name='celery_uid',
            field=models.UUIDField(null=True),
        ),
        migrations.AlterField(
            model_name='exporttask',
            name='uid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
    ]
