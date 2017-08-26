# noqa
# -*- coding: utf-8 -*-

import logging
import os
import shutil
import traceback

from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.utils import timezone
from django.utils.text import slugify

from celery import shared_task
from raven import Client

from jobs.models import Job, HDXExportRegion
from tasks.models import ExportRun, ExportTask

from utils import map_names_to_formats
from utils.manager import RunManager, Zipper

from .email import (
    send_completion_notification,
    send_error_notification,
    send_hdx_completion_notification,
    send_hdx_error_notification,
)

client = Client()

LOG = logging.getLogger(__name__)

class ExportTaskRunner(object):
    def run_task(self, job_uid=None, user=None): # noqa
        LOG.debug('Running Job with id: {0}'.format(job_uid))
        job = Job.objects.get(uid=job_uid)
        if not user:
            user = job.user
        run = ExportRun.objects.create(job=job, user=user, status='SUBMITTED')
        run.save()
        run_uid = str(run.uid)
        LOG.debug('Saved run with id: {0}'.format(run_uid))

        for format_name in job.export_formats:
            ExportTask.objects.create(
                run=run,
                status='PENDING',
                name=format_name
            )
            LOG.debug('Saved task: {0}'.format(format_name))

        run_task_remote.delay(run_uid)
        return run

@shared_task(bind=True, ignore_result=True)
def run_task_remote(self, run_uid): # noqa
    run = ExportRun.objects.get(uid=run_uid)
    run.status = 'RUNNING'
    run.started_at = timezone.now()
    run.save()
    LOG.debug('Running ExportRun with id: {0}'.format(run_uid))
    job = run.job

    try:
        stage_dir = os.path.join(settings.EXPORT_STAGING_ROOT, str(run_uid)) + '/'
        if not os.path.exists(stage_dir):
            os.makedirs(stage_dir, 6600)
        run_dir = os.path.join(settings.EXPORT_DOWNLOAD_ROOT, run_uid)
        if not os.path.exists(run_dir):
            os.makedirs(run_dir)

        aoi = job.simplified_geom
        feature_selection = job.feature_selection_object

        export_formats = map_names_to_formats(job.export_formats)

        download_dir = os.path.join(settings.EXPORT_DOWNLOAD_ROOT,run_uid)
        zipper = Zipper(
            slugify(job.name, allow_unicode=True), stage_dir, download_dir, aoi, feature_selection)

        def on_task_start(formatcls):
            LOG.debug('Task Start: {0} for run: {1}'.format(formatcls.name, run_uid))
            if formatcls in export_formats:
                task = ExportTask.objects.get(run__uid=run_uid, name=formatcls.name)
                task.status = 'RUNNING'
                task.started_at = timezone.now()
                task.save()


        def on_task_success(formatcls,results):
            LOG.debug('Task Success: {0} for run: {1}'.format(formatcls.name, run_uid))
            if formatcls in export_formats:
                task = ExportTask.objects.get(run__uid=run_uid, name=formatcls.name)
                zipfiles = zipper.run(results)
                task.filesize_bytes = sum(os.stat(zipfile).st_size for zipfile in zipfiles)
                task.filenames = [os.path.basename(zipfile) for zipfile in zipfiles]
                task.status = 'SUCCESS'
                task.finished_at = timezone.now()
                task.save()

        r = RunManager(
                export_formats,
                aoi,
                feature_selection,
                stage_dir,
                map_creator_dir=settings.OSMAND_MAP_CREATOR_DIR,
                garmin_splitter=settings.GARMIN_SPLITTER,
                garmin_mkgmap=settings.GARMIN_MKGMAP,
                per_theme=job.per_theme,
                on_task_start=on_task_start,
                on_task_success=on_task_success,
                overpass_api_url=settings.OVERPASS_API_URL,
                mbtiles_maxzoom=job.mbtiles_maxzoom,
                mbtiles_minzoom=job.mbtiles_minzoom,
                mbtiles_source=job.mbtiles_source,
            )
        r.run()

        public_dir = settings.HOSTNAME + os.path.join(settings.EXPORT_MEDIA_ROOT, run_uid)

        if settings.SYNC_TO_HDX and HDXExportRegion.objects.filter(job_id=run.job_id).exists():
            LOG.debug("Adding resources to HDX")
            region = HDXExportRegion.objects.get(job_id=run.job_id)
            export_set = region.hdx_dataset
            export_set.sync_resources(zipper.zipped_resources,public_dir)

        if run.job.hdx_export_region_set.count() == 0:
            # not associated with an HDX Export Regon; send mail
            send_completion_notification(run)
        else:
            send_hdx_completion_notification(
                run, run.job.hdx_export_region_set.first())

        run.status = 'COMPLETED'
        LOG.debug('Finished ExportRun with id: {0}'.format(run_uid))
    except Exception as e:
        client.captureException(
            extra={
                'run_uid': run_uid,
            }
        )
        run.status = 'FAILED'
        LOG.warn('ExportRun {0} failed: {1}'.format(run_uid, e))
        LOG.warn(traceback.format_exc())

        send_error_notification(run)
        if run.job.hdx_export_region_set.count() > 0:
            send_hdx_error_notification(
                run, run.job.hdx_export_region_set.first())
    finally:
        shutil.rmtree(stage_dir)
        run.finished_at = timezone.now()
        run.save()
