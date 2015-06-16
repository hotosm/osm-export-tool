# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields.hstore


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0016_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(serialize=False, editable=False, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('geom_types', django.contrib.postgres.fields.hstore.HStoreField()),
            ],
        ),
        migrations.AddField(
            model_name='job',
            name='tags',
            field=models.ManyToManyField(related_name='tags', to='jobs.Tag'),
        ),
    ]
