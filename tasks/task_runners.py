# noqa
# -*- coding: utf-8 -*-

import logging
import os
import shutil
import traceback
import dramatiq
import django
from django.apps import apps
from django.conf import settings

if not apps.ready and not settings.configured:
    django.setup()

from django.contrib.gis.geos import GEOSGeometry
from django.utils import timezone
from django.utils.text import slugify
from django.db import IntegrityError

from raven import Client

from jobs.models import Job, HDXExportRegion
from tasks.models import ExportRun, ExportTask

from .email import (
    send_completion_notification,
    send_error_notification,
    send_hdx_completion_notification,
    send_hdx_error_notification,
)

import time

import osm_export_tool
import osm_export_tool.tabular as tabular
import osm_export_tool.nontabular as nontabular
from osm_export_tool.mapping import Mapping
from osm_export_tool.geometry import load_geometry
from osm_export_tool.sources import Overpass

client = Client()

LOG = logging.getLogger(__name__)

class ExportTaskRunner(object):
    def run_task(self, job_uid=None, user=None, ondemand=True): # noqa
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

        if ondemand:
            run_task_async_ondemand.send(run_uid)
        else:
            run_task_async_scheduled.send(run_uid)
        return run

@dramatiq.actor(max_retries=0,queue_name='default',time_limit=7200000)
def run_task_async_ondemand(run_uid):
    run_task_remote(run_uid)

@dramatiq.actor(max_retries=0,queue_name='scheduled',time_limit=7200000)
def run_task_async_scheduled(run_uid):
    run_task_remote(run_uid)

def run_task_remote(run_uid):
    stage_dir = os.path.join(settings.EXPORT_STAGING_ROOT, str(run_uid)) + '/'

    run = ExportRun.objects.get(uid=run_uid)
    run.status = 'RUNNING'
    run.started_at = timezone.now()
    run.save()

    LOG.debug('Running ExportRun with id: {0}'.format(run_uid))
    job = run.job

    # set up staging and download directories
    if not os.path.exists(stage_dir):
        os.makedirs(stage_dir, 6600)
    run_dir = os.path.join(settings.EXPORT_DOWNLOAD_ROOT, run_uid)

    if not os.path.exists(run_dir):
        os.makedirs(run_dir)

    # prepare to call osm_export_tool
    geom = load_geometry(job.simplified_geom.json)
    export_formats = job.export_formats
    download_dir = os.path.join(settings.EXPORT_DOWNLOAD_ROOT,run_uid)
    mapping = Mapping(job.feature_selection)

    def start_task(name):
        LOG.debug('Task Start: {0} for run: {1}'.format(name, run_uid))
        task = ExportTask.objects.get(run__uid=run_uid, name=name)
        task.status = 'RUNNING'
        task.started_at = timezone.now()
        task.save()

    def finish_task(name):
        LOG.debug('Task Finish: {0} for run: {1}'.format(name, run_uid))
        task = ExportTask.objects.get(run__uid=run_uid, name=name)
        task.status = 'SUCCESS'
        task.finished_at = timezone.now()
        task.save()

    tabular_outputs = []
    if 'geopackage' in export_formats:
        tabular_outputs.append(tabular.Geopackage(os.path.join(stage_dir,'test_gpkg'),mapping))
        start_task('geopackage')

    if 'shapefile' in export_formats:
        tabular_outputs.append(tabular.Shapefile(os.path.join(stage_dir,'test_shp'),mapping))
        start_task('shapefile')

    if 'kml' in export_formats:
        tabular_outputs.append(tabular.Kml(os.path.join(stage_dir,'test_kml'),mapping))
        start_task('kml')

    h = tabular.Handler(tabular_outputs,mapping)
    source = Overpass('http://overpass.hotosm.org',geom,os.path.join(stage_dir,'overpass.osm.pbf'),tempdir=stage_dir)
    h.apply_file(source.path(), locations=True, idx='sparse_file_array')

    for output in tabular_outputs:
        output.finalize()

    if 'geopackage' in export_formats:
        finish_task('geopackage')

    if 'shapefile' in export_formats:
        finish_task('shapefile')

    if 'kml' in export_formats:
        finish_task('kml')

    run.status = 'COMPLETED'
    run.finished_at = timezone.now()
    run.save()
    LOG.debug('Finished ExportRun with id: {0}'.format(run_uid))