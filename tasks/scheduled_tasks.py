import datetime
import logging

from django.utils import timezone

from celery import Task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

class PurgeUnpublishedExportsTask(Task):
    
    name = "Purge Unpublished Exports"
    
    def run(self,):
        from jobs.models import Job
        time_limit = timezone.now() - timezone.timedelta(hours=48)
        expired_jobs = Job.objects.filter(created_at__lt=time_limit, published=False)
        count = expired_jobs.count()
        logger.debug('Purging {0} unpublished exports.'.format(count))
        expired_jobs.delete()
