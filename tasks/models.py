from __future__ import unicode_literals
import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User, Group
from jobs.models import Job


class TimeStampedModelMixin(models.Model):
    """
    Mixin for timestamped models.
    """
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
    celery_uid = models.UUIDField(null=True) # celery task uid
    name = models.CharField(max_length=50)
    run = models.ForeignKey(ExportRun, related_name='tasks')
    status = models.CharField(blank=True, max_length=20, db_index=True)
    started_at = models.DateTimeField(editable=False, null=True)
    finished_at = models.DateTimeField(editable=False, null=True)

    class Meta:
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
