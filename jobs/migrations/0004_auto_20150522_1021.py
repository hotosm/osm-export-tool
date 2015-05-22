# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0003_auto_20150522_1011'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exportformat',
            name='slug',
            field=models.SlugField(unique=True, max_length=10),
        ),
    ]
