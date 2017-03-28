# -*- coding: utf-8 -*-
from celery import Task
from celery.utils.log import get_task_logger
import dateutil.parser
from django.conf import settings
from django.utils import timezone
import requests

from core.celery import app


LOG = get_task_logger(__name__)


class PurgeUnpublishedExportsTask(Task):
    """
    Purge unpublished export tasks after 48 hours.
    """

    name = "Purge Unpublished Exports"

    def run(self,):
        from jobs.models import Job
        time_limit = timezone.now() - timezone.timedelta(hours=48)
        expired_jobs = Job.objects.filter(created_at__lt=time_limit, published=False)
        count = expired_jobs.count()
        LOG.debug('Purging {0} unpublished exports.'.format(count))
        expired_jobs.delete()
