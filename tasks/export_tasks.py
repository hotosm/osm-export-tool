from __future__ import absolute_import

import logging
import time
from celery import app, shared_task, Task
from celery.registry import tasks
from celery.contrib.methods import task
from celery.utils.log import get_task_logger
from django.utils import timezone
from hot_exports import settings
from jobs.models import Job

# Get an instance of a logger
logger = get_task_logger(__name__)

class TaskRunner(object):
    """
    Abstract base class for running tasks
    """

    class Meta:
        abstract = True


class ExportTaskRunner(TaskRunner):
    """
    Runs HOT Export Tasks
    """
    export_registry = settings.EXPORT_TASKS
    
    def run_task(self, job_uid=None):
        logger.debug('Running Job with id: {0}'.format(job_uid))
        job = Job.objects.get(uid=job_uid)
        formats = job.formats.all()
        shp_export_task = SHPExportTask()
        result = shp_export_task.delay(job_uid=job_uid)
        job.status = result.state
        job.save()


class ExportTask(Task):
    """
    Abstract base class for export tasks.
    """
    class Meta:
        abstract = True
        
    def __call__(self, *args, **kwargs):
        """In celery task this function call the run method, here you can
        set some environment variable before the run of the task"""
        logger.info("Starting to run")
        return self.run(*args, **kwargs)
        
    def on_success(self, retval, task_id, args, kwargs):
        job_uid = kwargs['job_uid']
        job = Job.objects.get(uid=job_uid)
        job.status = 'SUCCESS'
        job.updated_at = timezone.now()
        job.save()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.debug('failed')
        
    def after_return(self, *args, **kwargs):
        logger.debug('Task returned: {0!r}'.format(self.request))


class SHPExportTask(ExportTask):
    
    def run(self, job_uid=None):
        
        # dummy task for now..
        time.sleep(10)
        logger.debug('Job ran {0}'.format(job_uid))

