# noqa
# -*- coding: utf-8 -*-

import os
import shutil
from datetime import datetime, timedelta

import pytz
from core.celery import app
from django.conf import settings
from django.utils import timezone
from jobs.models import HDXExportRegion

from .models import ExportRun
from .task_runners import ExportTaskRunner


@app.task(ignore_result=True, name='Queue Periodic Runs')
def queue_periodic_job_runs(): # noqa
    now = timezone.now()

    for region in HDXExportRegion.objects.exclude(schedule_period='disabled'):
        last_run = region.job.runs.last()
        if last_run:
            last_run_at = last_run.created_at
        else:
            last_run_at = datetime.fromtimestamp(0, pytz.timezone('UTC'))

        delta = now - last_run_at

        # if it's been too long or it's the regularly-scheduled time
        if (delta > region.delta) or \
            (region.schedule_period == '6hrs' and
                (now.hour - region.schedule_hour) % 6 == 0 and
                delta > timedelta(hours=2)) or \
            (region.schedule_period == 'daily' and
                region.schedule_hour == now.hour and
                delta > timedelta(hours=2)) or \
            (region.schedule_period == 'weekly' and
                (now.weekday() + 1) % 7 == 0 and
                region.schedule_hour == now.hour and
                delta > timedelta(hours=2)) or \
            (region.schedule_period == 'monthly' and
                now.day == 1 and
                region.schedule_hour == now.hour and
                delta > timedelta(hours=2)):
            ExportTaskRunner().run_task(job_uid=region.job.uid,queue="celery-scheduled")


@app.task(ignore_result=True, name="Remove Old Downloads")
def remove_old_downloads():
    for run in ExportRun.objects.raw("""
SELECT
    id,
    uid
FROM (
    SELECT
        export_runs.id,
        export_runs.uid,
        export_runs.created_at,
        rank() OVER
            (PARTITION BY job_id ORDER BY export_runs.created_at DESC) AS rank
    FROM export_runs
    LEFT JOIN jobs ON jobs.id = export_runs.job_id
    WHERE status='COMPLETED'
        AND expire_old_runs = true
) AS _
WHERE rank > 1
  AND created_at < NOW() - INTERVAL '2 weeks'
    """):
        shutil.rmtree(
            os.path.join(settings.EXPORT_DOWNLOAD_ROOT, str(run.uid)), True)
