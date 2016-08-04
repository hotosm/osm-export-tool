# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import shutil
import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from django.utils import timezone

from oet2.jobs.models import Job

logger = logging.getLogger(__name__)


class TimeStampedModelMixin(models.Model):
    """
    Mixin for timestamped models.
    """
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    started_at = models.DateTimeField(default=timezone.now, editable=False)
    finished_at = models.DateTimeField(editable=False, null=True)

    class Meta:
        abstract = True


class RunModelMixin(TimeStampedModelMixin):
    """
    Mixin for task runs.
    """
    id = models.AutoField(primary_key=True, editable=False)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class ExportRun(RunModelMixin):
    """
    Model for export task runs.
    """
    job = models.ForeignKey(Job, related_name='runs')
    user = models.ForeignKey(User, related_name="runs", default=0)
    status = models.CharField(
        blank=True, max_length=20,
        db_index=True, default=''
    )

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
    celery_uid = models.UUIDField(null=True)  # celery task uid
    name = models.CharField(max_length=50)
    run = models.ForeignKey(ExportRun, related_name='tasks')
    status = models.CharField(blank=True, max_length=20, db_index=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    started_at = models.DateTimeField(editable=False, null=True)
    finished_at = models.DateTimeField(editable=False, null=True)

    class Meta:
        ordering = ['created_at']
        managed = True
        db_table = 'export_tasks'

    def __str__(self):
        return 'ExportTask uid: {0}'.format(self.uid)


class ExportTaskResult(models.Model):
    task = models.OneToOneField(ExportTask, primary_key=True, related_name='result')
    filename = models.CharField(max_length=100, blank=True, editable=False)
    size = models.FloatField(null=True, editable=False)
    download_url = models.URLField(
        verbose_name='Url to export task result output.',
        max_length=254
    )

    class Meta:
        managed = True
        db_table = 'export_task_results'

    def __str__(self):
        return 'ExportTaskResult uid: {0}'.format(self.task.uid)


class ExportTaskException(models.Model):
    """
    Model to store ExportTask exceptions for auditing.
    """
    id = models.AutoField(primary_key=True, editable=False)
    task = models.ForeignKey(ExportTask, related_name='exceptions')
    timestamp = models.DateTimeField(default=timezone.now, editable=False)
    exception = models.TextField(editable=False)

    class Meta:
        managed = True
        db_table = 'export_task_exceptions'


@receiver(post_delete, sender=ExportRun)
def exportrun_delete_exports(sender, instance, **kwargs):
    """
    Delete the associated export files when a ExportRun is deleted.
    """
    download_root = settings.EXPORT_DOWNLOAD_ROOT
    run_uid = instance.uid
    run_dir = '{0}{1}'.format(download_root, run_uid)
    shutil.rmtree(run_dir, ignore_errors=True)
