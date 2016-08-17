# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('jobs', '0009_job_configs'),
    ]

    operations = [
        migrations.AddField(
            model_name='exportconfig',
            name='user',
            field=models.ForeignKey(related_name='user', default='', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='job',
            name='user',
            field=models.ForeignKey(related_name='owner', to=settings.AUTH_USER_MODEL),
        ),
    ]
