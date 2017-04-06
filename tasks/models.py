# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import shutil
import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from django.utils import timezone

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
        managed = True
        db_table = 'export_runs'

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
    filename = models.CharField(max_length=50,null=True)

    class Meta:
        ordering = ['created_at']
        managed = True
        db_table = 'export_tasks'

    def __str__(self):
        return 'ExportTask uid: {0}'.format(self.uid)


@receiver(post_delete, sender=ExportRun)
def exportrun_delete_exports(sender, instance, **kwargs):
    """
    Delete the associated export files when a ExportRun is deleted.
    """
    download_root = settings.EXPORT_DOWNLOAD_ROOT
    run_uid = instance.uid
    run_dir = '{0}{1}'.format(download_root, run_uid)
    shutil.rmtree(run_dir, ignore_errors=True)
