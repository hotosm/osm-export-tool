from __future__ import unicode_literals
import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User, Group
from django.db.models.fields import CharField

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


class ExportFormat(models.Model):
    """Model for a ExportFormat"""
    id = models.AutoField(primary_key=True, editable=False)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = LowerCaseCharField(max_length=7, unique=True, default='')
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
    
    def __unicode__(self, ):
        return '{0}'.format(self.slug)
    
   

class Job(models.Model):
    """Model for a Job"""
    id = models.AutoField(primary_key=True, editable=False)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
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
    id = models.AutoField(primary_key=True, editable=False)
    uid = models.UUIDField(blank=True) # celery task id
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now, editable=False)
    job = models.ForeignKey(Job, related_name='job')
    


    
