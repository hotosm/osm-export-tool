# -*- coding: utf-8 -*-
import importlib
import logging
import os
import re
import shutil
from datetime import datetime, timedelta

from django.conf import settings
from django.db import DatabaseError
from django.contrib.gis.geos import GEOSGeometry
from django.utils import timezone

from celery import shared_task
from raven import Client

from jobs.models import Job, HDXExportRegion
from tasks.models import ExportRun, ExportTask

from feature_selection.feature_selection import FeatureSelection

from utils import FORMAT_NAMES
from utils.osm_xml import OSM_XML
from utils.osm_pbf import OSM_PBF
from utils.geopackage import Geopackage
from utils.kml import KML
from utils.shp import Shapefile
from utils.theme_gpkg import ThematicGPKG
from utils.theme_shp import ThematicSHP

client = Client()

# Get an instance of a logger
LOG = logging.getLogger(__name__)

class ExportTaskRunner(object):
    """
    Runs HOT Export Tasks
    """
    def run_task(self, job_uid=None, user=None):
        run_uid = ''
        LOG.debug('Running Job with id: {0}'.format(job_uid))
        # pull the job from the database
        job = Job.objects.get(uid=job_uid)
        job_name = normalize_job_name(job.name)

        # build a list of celery tasks based on the export formats..
        export_tasks = job.export_formats

        assert len(export_tasks) > 0
        # add the new run
        if not user:
            user = job.user
        # add the export run to the database
        run = ExportRun.objects.create(job=job, user=user, status='SUBMITTED')  # persist the run
        run.save()
        run_uid = str(run.uid)
        LOG.debug('Saved run with id: {0}'.format(run_uid))

        for task in [OSM_XML,OSM_PBF,Geopackage,KML,Shapefile,ThematicGPKG,ThematicSHP]:
            ExportTask.objects.create(run=run,status='PENDING',name=task.name)
            LOG.debug('Saved task: {0}'.format(task.name))
        run_task_remote.delay(run_uid)
        return run


def normalize_job_name(name):
    # Remove all non-word characters
    s = re.sub(r"[^\w\s]", '', name)
    # Replace all whitespace with a single underscore
    s = re.sub(r"\s+", '_', s)
    return s.lower()


def report_started_task(run_uid,task_name):
    task = ExportTask.objects.get(run__uid=run_uid, name=task_name)
    task.status = 'RUNNING'
    task.started_at = timezone.now()
    task.save()
    LOG.debug('Updated task: {0} for run: {1}'.format(task_name, run_uid))

def report_finished_task(run_uid,task_name,results):
    task = ExportTask.objects.get(run__uid=run_uid, name=task_name)
    task.filesize_bytes = sum(os.stat(result).st_size for result in results)
    task.filenames = [os.path.basename(result) for result in results]
    task.status = 'SUCCESS'
    task.finished_at = timezone.now()
    task.save()
    LOG.debug('Updated task: {0} for run: {1}'.format(task_name, run_uid))


SIMPLE = '''
waterways:
    types: 
        - lines
        - polygons
    select:
        - name
        - waterway
buildings:
    types:
        - lines
        - polygons
    select:
        - name
        - building
    where: building IS NOT NULL
'''

@shared_task
def run_task_remote(run_uid):
    run = ExportRun.objects.get(uid=run_uid)
    run.status = 'RUNNING'
    run.started_at = timezone.now()
    run.save()
    LOG.debug('Running ExportRun with id: {0}'.format(run_uid))
    job = run.job
    job_name = normalize_job_name(job.name)
    export_tasks = job.export_formats

    # setup the staging directory
    stage_dir = os.path.join(settings.EXPORT_STAGING_ROOT, str(run_uid)) + '/'
    os.makedirs(stage_dir, 6600)

    aoi = GEOSGeometry(job.the_geom)
    try:
        feature_selection = job.feature_selection_object
    except:
        feature_selection = FeatureSelection(SIMPLE)

    osm_xml = OSM_XML(aoi,stage_dir + "osm_xml.osm")
    osm_pbf = OSM_PBF(stage_dir + "osm_xml.osm",stage_dir + "osm_pbf.pbf")
    geopackage = Geopackage(stage_dir + "osm_pbf.pbf",stage_dir + "geopackage.gpkg",stage_dir+"osmconf.ini",feature_selection)
    kml = KML(stage_dir + "geopackage.gpkg",stage_dir + "kml.kmz")
    shp = Shapefile(stage_dir + "geopackage.gpkg",stage_dir + "shapefile.shp.zip")
    thematic_gpkg = ThematicGPKG(stage_dir+"geopackage.gpkg",feature_selection)
    thematic_shp = ThematicSHP(stage_dir+"geopackage.gpkg",stage_dir,feature_selection)

    for task in [osm_xml,osm_pbf,geopackage,kml,shp,thematic_gpkg,thematic_shp]:
        report_started_task(run_uid, task.name)
        task.run()
        report_finished_task(run_uid, task.name,task.results)

    for task in [osm_xml,osm_pbf,geopackage,kml,shp,thematic_gpkg,thematic_shp]:
        run_dir = os.path.join(settings.EXPORT_DOWNLOAD_ROOT, run_uid)
        if not os.path.exists(run_dir):
            os.makedirs(run_dir)
        for result in task.results:
            filename = os.path.basename(result)
            download_path = os.path.join(settings.EXPORT_DOWNLOAD_ROOT, run_uid, filename)
            shutil.copy(result, download_path)

    run.status = 'COMPLETED'
    run.finished_at = timezone.now()
    run.save()
    LOG.debug('Finished ExportRun with id: {0}'.format(run_uid))

    
    if  HDXExportRegion.objects.filter(job_id=run.job_id).exists():
        LOG.debug("Adding resources to HDX")
        region = HDXExportRegion.objects.get(job_id=run.job_id)
        export_set = region.hdx_dataset
        for theme in feature_selection.themes:
            resources = []
            for geom_type in feature_selection.geom_types(theme):
                resources.append({
                    'name': theme + ' ' + geom_type,
                    'format': 'zipped shapefile',  
                    'description': "ESRI Shapefile of " + geom_type,
                    'url': settings.HOSTNAME + os.path.join(settings.EXPORT_MEDIA_ROOT,run_uid,theme + '_' + geom_type + ".zip")
                })
            export_set.datasets[theme].add_update_resources(resources)
        export_set.sync_datasets()


    # finalize the task
    #shutil.rmtree(stage_dir)
    # send mail

    #except Exception as exc:
    #    print exc
    #    client.captureException(
    #        extra={
    #            'run_uid': run_uid,
    #            'task': exc,
    #        }
    #    )
