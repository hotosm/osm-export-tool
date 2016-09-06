# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0008_auto_20150905_0952'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='description',
            field=models.CharField(max_length=1000, db_index=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='feature_pub',
            field=models.BooleanField(default=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='feature_save',
            field=models.BooleanField(default=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='name',
            field=models.CharField(max_length=100, db_index=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='published',
            field=models.BooleanField(default=False, db_index=True),
        ),
    ]
