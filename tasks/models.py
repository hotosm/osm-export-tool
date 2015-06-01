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
    finished_at = models.DateTimeField(default=timezone.now, editable=False)
    
    class Meta:
        abstract = True


class RunModelMixin(TimeStampedModelMixin):
    """
    Mixin for task runs.
    """
    id = models.AutoField(primary_key=True, editable=False)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=20, db_index=True)
    
    class Meta:
        abstract = True


class ExportRun(RunModelMixin):
    """
    Model for export task runs.
    """
    job = models.ForeignKey(Job, related_name='runs')
    
    class Meta:
        managed = True
        db_table = 'export_runs'
    
    def save(self, *args, **kwargs):
        self.type = 'EXPORT'
        super(ExportRun, self).save(*args, **kwargs)
        
    def __str__(self):
        return '{0}'.format(self.uid)


class ExportTask(TimeStampedModelMixin):
    """
    Model for an ExportTask.
    """
    id = models.AutoField(primary_key=True, editable=False)
    uid = models.UUIDField(blank=True) # celery task id
    run = models.ForeignKey(ExportRun, related_name='tasks')
    
    class Meta:
        managed = True
        db_table = 'export_tasks'
    
    def __str__(self):
        return 'ExportTask uid: {0}'.format(self.uid)


class ExportTaskResult(models.Model):
    task = models.OneToOneField(ExportTask, primary_key=True, related_name='result')
    output_url = models.URLField(verbose_name='Url to export task result.')
    
    class Meta:
        managed = True
        db_table = 'export_task_results'
    
    def __str__(self):
        return 'ExportTaskResult uid: {0}'.format(self.task.uid)
    