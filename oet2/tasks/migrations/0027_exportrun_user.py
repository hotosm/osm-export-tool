# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tasks', '0026_auto_20150724_1437'),
    ]

    operations = [
        migrations.AddField(
            model_name='exportrun',
            name='user',
            field=models.ForeignKey(related_name='runs', default=0, to=settings.AUTH_USER_MODEL),
        ),
    ]
