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
                    (region.schedule_period == '2wks' and
                        now.day in (15, 1) and
                        region.schedule_hour == now.hour and
                        delta > timedelta(hours=2)) or \
                    (region.schedule_period == '3wks' and
                        now.day == 21 and
                        region.schedule_hour == now.hour and
                        delta > timedelta(hours=2)) or \
                    (region.schedule_period == 'monthly' and
                        now.day == 1 and
                        region.schedule_hour == now.hour and
                        delta > timedelta(hours=2)):
                    ExportTaskRunner().run_task(job_uid=region.job.uid,ondemand=False)



