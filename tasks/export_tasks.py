from __future__ import absolute_import

import logging
import time
from celery import app, shared_task, Task
from celery.utils.log import get_task_logger
from django.utils import timezone
from jobs.models import Job

# Get an instance of a logger
logger = get_task_logger(__name__)


class ExportTaskRunner(object):
    pass

    




class HOTExportTask(Task):
    
    class Meta:
        abstract = True
        
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



@shared_task(base=HOTExportTask)
def run_export_job(job_uid=None):
    logger.debug('Running Job with id: {0}'.format(job_uid))
    job = Job.objects.get(uid=job_uid)
    job.status = 'RUNNING'
    job.save()
    time.sleep(10)
    logger.debug('Job ran {0}'.format(job_uid))
   


