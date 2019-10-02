# noqa
# -*- coding: utf-8 -*-

import logging
import os
from os.path import join, exists, basename
import shutil

import django
from django.apps import apps
from django.conf import settings

if not apps.ready and not settings.configured:
    django.setup()

import dramatiq
from raven import Client

from django.utils import timezone
from django.utils.text import get_valid_filename

from jobs.models import Job
from tasks.models import ExportRun, ExportTask

import osm_export_tool
import osm_export_tool.tabular as tabular
import osm_export_tool.nontabular as nontabular
from osm_export_tool.mapping import Mapping
from osm_export_tool.geometry import load_geometry
from osm_export_tool.sources import Overpass
from osm_export_tool.package import create_package


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
    stage_dir = join(settings.EXPORT_STAGING_ROOT, run_uid)
    download_dir = join(settings.EXPORT_DOWNLOAD_ROOT,run_uid)
    if not exists(stage_dir):
        os.makedirs(stage_dir)
    if not exists(download_dir):
        os.makedirs(download_dir)

    run = ExportRun.objects.get(uid=run_uid)
    run.status = 'RUNNING'
    run.started_at = timezone.now()
    run.save()

    LOG.debug('Running ExportRun with id: {0}'.format(run_uid))
    job = run.job
    valid_name = get_valid_filename(job.name)

    geom = load_geometry(job.simplified_geom.json)
    export_formats = job.export_formats
    mapping = Mapping(job.feature_selection)

    def start_task(name):
        LOG.debug('Task Start: {0} for run: {1}'.format(name, run_uid))
        task = ExportTask.objects.get(run__uid=run_uid, name=name)
        task.status = 'RUNNING'
        task.started_at = timezone.now()
        task.save()

    def finish_task(name,created_file):
        LOG.debug('Task Finish: {0} for run: {1}'.format(name, run_uid))
        task = ExportTask.objects.get(run__uid=run_uid, name=name)
        task.status = 'SUCCESS'
        task.finished_at = timezone.now()
        task.filenames = [basename(part) for part in created_file.parts]
        task.filesize_bytes = created_file.size()
        task.save()

    geopackage = None
    shp = None
    kml = None

    tabular_outputs = []
    if 'geopackage' in export_formats:
        geopackage = tabular.Geopackage(join(stage_dir,'test_gpkg'),mapping)
        tabular_outputs.append(geopackage)
        start_task('geopackage')

    if 'shp' in export_formats:
        shp = tabular.Shapefile(join(stage_dir,'test_shp'),mapping)
        tabular_outputs.append(shp)
        start_task('shp')

    if 'kml' in export_formats:
        kml = tabular.Kml(join(stage_dir,'test_kml'),mapping)
        tabular_outputs.append(kml)
        start_task('kml')

    h = tabular.Handler(tabular_outputs,mapping)
    source = Overpass('http://overpass.hotosm.org',geom,join(stage_dir,'overpass.osm.pbf'),tempdir=stage_dir)


    h.apply_file(source.path(), locations=True, idx='sparse_file_array')

    if geopackage:
        geopackage.finalize()
        zips = create_package(join(download_dir,valid_name + '_gpkg.zip'),geopackage.files,boundary_geom=geom)
        finish_task('geopackage',zips)

    if shp:
        shp.finalize()
        zips = create_package(join(download_dir,valid_name + '_shp.zip'),shp.files,boundary_geom=geom)
        finish_task('shp',zips)

    if kml:
        kml.finalize()
        zips = create_package(join(download_dir,valid_name + '_kml.zip'),kml.files,boundary_geom=geom)
        finish_task('kml',zips)

    if 'garmin_img' in export_formats:
        start_task('garmin_img')
        garmin_files = nontabular.garmin(source.path(),settings.GARMIN_SPLITTER,settings.GARMIN_MKGMAP,tempdir=stage_dir)
        zips = create_package(join(download_dir,valid_name + '_gmapsupp_img.zip'),garmin_files,boundary_geom=geom)
        finish_task('garmin_img',zips)

    if 'mwm' in export_formats:
        start_task('mwm')
        mwm_files = nontabular.mwm(source.path(),join(stage_dir,'mwm'),settings.GENERATE_MWM,settings.GENERATOR_TOOL)
        zips = create_package(join(download_dir,valid_name + '_mwm.zip'),mwm_files,boundary_geom=geom)
        finish_task('mwm',zips)

    if 'osmand_obf' in export_formats:
        start_task('osmand_obf')
        osmand_files = nontabular.osmand(source.path(),settings.OSMAND_MAP_CREATOR_DIR,tempdir=stage_dir)
        zips = create_package(join(download_dir,valid_name + '_Osmand2_obf.zip'),osmand_files,boundary_geom=geom)
        finish_task('osmand_obf',zips)

    if 'mbtiles' in export_formats:
        start_task('mbtiles')
        mbtiles_files = nontabular.mbtiles(geom,join(stage_dir,valid_name + '.mbtiles'),job.mbtiles_source,job.mbtiles_minzoom,job.mbtiles_maxzoom)
        zips = create_package(join(download_dir,valid_name + '_mbtiles.zip'),mbtiles_files,boundary_geom=geom)
        finish_task('mbtiles',zips)

    # do this last so we can do a mv instead of a copy
    if 'osm_pbf' in export_formats:
        start_task('osm_pbf')
        target = join(download_dir,valid_name + '.osm.pbf')
        shutil.move(source.path(),target)
        finish_task('osm_pbf',osm_export_tool.File('pbf',[target],''))

    run.status = 'COMPLETED'
    run.finished_at = timezone.now()
    run.save()
    LOG.debug('Finished ExportRun with id: {0}'.format(run_uid))