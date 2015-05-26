# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0002_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='region',
            field=models.OneToOneField(null=True, to='jobs.Region'),
        ),
    ]
