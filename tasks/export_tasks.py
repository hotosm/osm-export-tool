from __future__ import absolute_import

import logging
import time
import sys
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
        formats = [format.slug for format in job.formats.all()]
        # pick the export task based on the format..
        for format in formats:
            try:
                # see settings.EXPORT_TASKS for configuration
                class_name = self.export_registry[format]
                """
                Instantiate the required class.
                Assuming for now that ExportTasks will be in this module.
                """
                export_task = getattr(sys.modules[__name__], class_name)()
                result = export_task.delay(job_uid=job_uid)
                job.status = result.state
                job.save()
            except KeyError as e:
                logger.debug(e)
                #TODO: how to report errors here?


# ExportTask abstract base class and subclasses.

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


class ShpExportTask(ExportTask):
    """
    Class defining SHP export function.
    """
    def run(self, job_uid=None):
        
        # dummy task for now..
        # logic for SHP export goes here..
        time.sleep(10)
        logger.debug('Job ran {0}'.format(job_uid))


class KmlExportTask(ExportTask):
    """
    Class defining KML export function.
    """
    def run(self, job_uid=None):
       
       # dummy task for now..
       # logic for SHP export goes here..
       time.sleep(10)
       logger.debug('Job ran {0}'.format(job_uid))


class ObfExportTask(ExportTask):
    """
    Class defining OBF export function.
    """
    def run(self, job_uid=None):
       
       # dummy task for now..
       # logic for SHP export goes here..
       time.sleep(10)
       logger.debug('Job ran {0}'.format(job_uid))



class SqliteExportTask(ExportTask):
    """
    Class defining SQLITE export function.
    """
    def run(self, job_uid=None):
       
       # dummy task for now..
       # logic for SHP export goes here..
       time.sleep(10)
       logger.debug('Job ran {0}'.format(job_uid))


class PgdumpExportTask(ExportTask):
    """
    Class defining PGDUMP export function.
    """
    def run(self, job_uid=None):
       
       # dummy task for now..
       # logic for SHP export goes here..
       time.sleep(10)
       logger.debug('Job ran {0}'.format(job_uid))


class GarminExportTask(ExportTask):
    """
    Class defining GARMIN export function.
    """
    def run(self, job_uid=None):
       
       # dummy task for now..
       # logic for SHP export goes here..
       time.sleep(10)
       logger.debug('Job ran {0}'.format(job_uid))



