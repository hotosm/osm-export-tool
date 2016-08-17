# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0023_delete_tag'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(serialize=False, editable=False, primary_key=True)),
                ('key', models.CharField(default='', max_length=30, db_index=True)),
                ('value', models.CharField(default='', max_length=30, db_index=True)),
                ('job', models.ForeignKey(related_name='tags', to='jobs.Job')),
            ],
            options={
                'db_table': 'tags',
                'managed': True,
            },
        ),
    ]
