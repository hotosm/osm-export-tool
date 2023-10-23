import os
import shutil
from datetime import datetime, timedelta
import pytz
from django.core.management.base import BaseCommand
from django.utils import timezone
from jobs.models import HDXExportRegion, PartnerExportRegion
from tasks.task_runners import ExportTaskRunner
from tasks.models import ExportRun
from django.conf import settings

class Command(BaseCommand):
    help = 'Displays current time'

    def handle(self, *args, **kwargs):

        now = timezone.now()


        for regioncls in [HDXExportRegion, PartnerExportRegion]:
            for region in regioncls.objects.exclude(schedule_period='disabled'):
                schedule_match = False
                last_run = region.job.runs.last()
                if last_run:
                    last_run_status=last_run.status
                    if last_run_status in ['RUNNING','SUBMITTED']:
                        continue
                if region.schedule_period == '6hrs':
                    schedule_match = (now.hour - region.schedule_hour) % 6 == 0
                elif region.schedule_period == 'daily':
                    schedule_match = region.schedule_hour == now.hour
                elif region.schedule_period == 'weekly':
                    schedule_match = (now.weekday() + 1) % 7 == 0 and region.schedule_hour == now.hour
                elif region.schedule_period == '2wks':
                    schedule_match = now.day in (15, 1) and region.schedule_hour == now.hour
                elif region.schedule_period == '3wks':
                    schedule_match = now.day == 21 and region.schedule_hour == now.hour
                elif region.schedule_period == 'monthly':
                    schedule_match = now.day == 1 and region.schedule_hour == now.hour

                if schedule_match:
                    ExportTaskRunner().run_task(job_uid=region.job.uid,ondemand=False)