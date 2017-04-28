# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from jobs.models import Job

class ExportRun(models.Model):
    """
    Model for export task runs.
    """
    id = models.AutoField(primary_key=True, editable=False)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    job = models.ForeignKey(Job, related_name='runs')
    user = models.ForeignKey(User, related_name="runs", default=0)

    status = models.CharField(
        blank=True, max_length=20,
        db_index=True, default=''
    )
    started_at = models.DateTimeField(default=timezone.now, editable=False)
    finished_at = models.DateTimeField(editable=False, null=True)

    class Meta:
        db_table = 'export_runs'
        ordering = ['created_at']

    def __str__(self):
        return '{0}'.format(self.uid)


class ExportTask(models.Model):
    """
    Model for an ExportTask.
    """
    id = models.AutoField(primary_key=True, editable=False)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    run = models.ForeignKey(ExportRun, related_name='tasks')
    status = models.CharField(blank=True, max_length=20, db_index=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    started_at = models.DateTimeField(editable=False, null=True)
    finished_at = models.DateTimeField(editable=False, null=True)
    filesize_bytes = models.IntegerField(null=True)
    filenames = ArrayField(models.TextField(null=True),default=list)

    class Meta:
        db_table = 'export_tasks'
        ordering = ['created_at']

    def __str__(self):
        return 'ExportTask uid: {0}'.format(self.uid)
