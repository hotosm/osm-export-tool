import os
import shutil
from django.core.management.base import BaseCommand
from tasks.models import ExportRun, HDXExportRegion, PartnerExportRegion
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta

class Command(BaseCommand):
    help = 'remove old downloads'

    def handle(self, *args, **kwargs):
        def remove_dir(s):
            shutil.rmtree(os.path.join(settings.EXPORT_DOWNLOAD_ROOT,run_uid),True)

        for run_uid in os.listdir(settings.EXPORT_DOWNLOAD_ROOT):
            try:
                run = ExportRun.objects.get(uid=run_uid)
                old = timezone.now() - run.created_at > timedelta(days=30)
                if old:
                    if HDXExportRegion.objects.filter(job_id=run.job_id).count() > 0 or PartnerExportRegion.objects.filter(job_id=run.job_id).count() > 0:
                        if ExportRun.objects.filter(job_id=run.job_id,status='COMPLETED',created_at__gt=run.created_at).count() > 0:
                            remove_dir(run_uid)
                    else:
                        remove_dir(run_uid)
            except (ExportRun.DoesNotExist, ValidationError):
                remove_dir(run_uid)

        # Remove not running folders from staging.
        staging_folders = os.listdir(settings.EXPORT_STAGING_ROOT)
        uids = [str(r.uid) for r in ExportRun.objects.exclude(status='RUNNING')]

        # Filter.
        uids = [r for r in uids if r in staging_folders]

        for uid in uids:
            folder_path = os.path.join(settings.EXPORT_STAGING_ROOT, uid)
            shutil.rmtree(folder_path, True)
