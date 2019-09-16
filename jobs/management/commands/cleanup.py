import os
import shutil
from django.core.management.base import BaseCommand
from tasks.models import ExportRun
from django.conf import settings

class Command(BaseCommand):
    help = 'remove old downloads'

    def handle(self, *args, **kwargs):
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