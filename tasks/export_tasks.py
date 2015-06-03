#from __future__ import absolute_import

import logging
import time
import sys
import cPickle
from celery import app, shared_task, Task
from celery.registry import tasks
from celery.contrib.methods import task
from celery.utils.log import get_task_logger
from django.utils import timezone

# Get an instance of a logger
logger = get_task_logger(__name__)


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
        from tasks.models import ExportTask, ExportTaskResult
        finished = timezone.now()
        output_url = retval['output_url']
        task = ExportTask.objects.get(uid=task_id)
        task.finished_at = finished
        task.status = 'SUCCESS'
        task.save()
        result = ExportTaskResult.objects.create(task=task, output_url=output_url)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        from tasks.models import ExportTask, ExportTaskException
        task = ExportTask.objects.get(uid=task_id)
        task.status = 'FAILURE'
        task.finished_at = timezone.now()
        task.save()
        exception = cPickle.dumps(einfo)
        ExportTaskException.objects.create(task=task, exception=exception)

    def after_return(self, *args, **kwargs):
        logger.debug('Task returned: {0}'.format(self.request))


class ShpExportTask(ExportTask):
    """
    Class defining SHP export function.
    """
    
    name = 'Shapefile Export'
    
    def run(self, job_uid=None):
        """
        # dummy task for now..
        # logic for SHP export goes here..
        time.sleep(10)
        logger.debug('Job ran {0}'.format(job_uid))
        return {'output_url': 'http://testserver/some/download/file.zip'}
        """
        raise Exception('some exception')

class KmlExportTask(ExportTask):
    """
    Class defining KML export function.
    """
    
    name = 'KML Export'
    
    def run(self, job_uid=None):
       
       # dummy task for now..
       # logic for SHP export goes here..
       time.sleep(10)
       logger.debug('Job ran {0}'.format(job_uid))
       return {'output_url': 'http://testserver/some/download/file.zip'}


class ObfExportTask(ExportTask):    
    """
    Class defining OBF export function.
    """
    name = 'OBF Export'
    
    def run(self, job_uid=None):
       
       # dummy task for now..
       # logic for SHP export goes here..
       time.sleep(10)
       logger.debug('Job ran {0}'.format(job_uid))
       return {'output_url': 'http://testserver/some/download/file.zip'}



class SqliteExportTask(ExportTask):
    """
    Class defining SQLITE export function.
    """
    
    name = 'SQLITE Export'
    
    def run(self, job_uid=None):
       
       # dummy task for now..
       # logic for SHP export goes here..
       time.sleep(10)
       logger.debug('Job ran {0}'.format(job_uid))
       return {'output_url': 'http://testserver/some/download/file.zip'}


class PgdumpExportTask(ExportTask):
    """
    Class defining PGDUMP export function.
    """
    
    name = 'PGDUMP Export'
    
    def run(self, job_uid=None):
       
       # dummy task for now..
       # logic for SHP export goes here..
       time.sleep(10)
       logger.debug('Job ran {0}'.format(job_uid))
       return {'output_url': 'http://testserver/some/download/file.zip'}


class GarminExportTask(ExportTask):
    """
    Class defining GARMIN export function.
    """
    
    name = 'Garmin Export'
    
    def run(self, job_uid=None):
       
       # dummy task for now..
       # logic for SHP export goes here..
       time.sleep(10)
       logger.debug('Job ran {0}'.format(job_uid))
       return {'output_url': 'http://testserver/some/download/file.zip'}



