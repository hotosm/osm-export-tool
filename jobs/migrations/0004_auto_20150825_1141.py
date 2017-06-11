# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.db.models.fields import CharField
import jobs.models

class LowerCaseCharField(CharField):
    """
    Defines a charfield which automatically converts all inputs to
    lowercase and saves.
    """

    def pre_save(self, model_instance, add):
        """
        Converts the string to lowercase before saving.
        """
        current_value = getattr(model_instance, self.attname)
        setattr(model_instance, self.attname, current_value.lower())
        return getattr(model_instance, self.attname)

class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0003_job_published'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exportformat',
            name='slug',
            field=LowerCaseCharField(default='', unique=True, max_length=10),
        ),
    ]
