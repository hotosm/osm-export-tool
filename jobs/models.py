from __future__ import unicode_literals
import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User, Group


class ExportFormat(models.Model):
    """Model for a ExportFormat"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now, editable=False)
    cmd = models.TextField(max_length=1000)
    objects = models.Manager()
    class Meta:
        managed = True
        db_table = 'export_formats'
    def __str__(self):
        return '{0}'.format(self.name)
   

class Job(models.Model):
    """Model for a Job"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name='user')
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now, editable=False)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=65000)
    status = models.CharField(max_length=30)
    formats = models.ManyToManyField(ExportFormat, related_name='formats')
    objects = models.Manager()
    class Meta:
        managed = True
        db_table = 'jobs'
    def __str__(self):
        return '{0}'.format(self.name)
    
    
class ExportTask(models.Model):
    "Model for an ExportTask"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now, editable=False)
    task_id = models.CharField(max_length=36, default='')
    job = models.ForeignKey(Job, related_name='job')
    


    
