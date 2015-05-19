from __future__ import absolute_import

import logging, time

from celery import shared_task, Task

from jobs.models import Job

# Get an instance of a logger
logger = logging.getLogger(__name__)


class HOTExportTask(Task):
    
    abstract = True
        
    def on_success(self, retval, task_id, args, kwargs):
        job = Job.objects.get(task_id=task_id)
        job.status = 'SUCCESS'
        job.save()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.debug('failed')
        
    def after_return(self, *args, **kwargs):
        logger.debug('Task returned: {0!r}'.format(self.request))



@shared_task(base=HOTExportTask)
def run_export_job(job_id):
    logger.debug('Running Job with id: {0}'.format(job_id))
    job = Job.objects.get(id=job_id)
    job.status = 'RUNNING'
    job.save()
    time.sleep(30)
    logger.debug('Job ran {0}'.format(job_id))
   


