# noqa
# -*- coding: utf-8 -*-

import logging
import os
import re
import shutil

from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.utils import timezone

from celery import shared_task
from raven import Client

from jobs.models import Job, HDXExportRegion
from tasks.models import ExportRun, ExportTask

from feature_selection.feature_selection import FeatureSelection

from utils.osm_xml import OSM_XML
from utils.osm_pbf import OSM_PBF
from utils.geopackage import Geopackage
from utils.kml import KML
from utils.theme_gpkg import ThematicGPKG
from utils.theme_shp import ThematicSHP

client = Client()

# Get an instance of a logger
LOG = logging.getLogger(__name__)


class ExportTaskRunner(object):
    """Runs HOT Export Tasks."""

    def run_task(self, job_uid=None, user=None): # noqa
        run_uid = ''
        LOG.debug('Running Job with id: {0}'.format(job_uid))
        # pull the job from the database
        job = Job.objects.get(uid=job_uid)

        # build a list of celery tasks based on the export formats..
        export_tasks = job.export_formats

        assert len(export_tasks) > 0
        # add the new run
        if not user:
            user = job.user
        # add the export run to the database
        # persist the run
        run = ExportRun.objects.create(job=job, user=user, status='SUBMITTED')
        run.save()
        run_uid = str(run.uid)
        LOG.debug('Saved run with id: {0}'.format(run_uid))

        for task in [OSM_XML, OSM_PBF, Geopackage, KML, ThematicGPKG,
                     ThematicSHP]:
            ExportTask.objects.create(
                run=run,
                status='PENDING',
                name=task.name
            )
            LOG.debug('Saved task: {0}'.format(task.name))
        run_task_remote.delay(run_uid)
        return run


def normalize_job_name(name): # noqa
    # Remove all non-word characters
    s = re.sub(r"[^\w\s]", '', name)
    # Replace all whitespace with a single underscore
    s = re.sub(r"\s+", '_', s)
    return s.lower()


def report_started_task(run_uid, task_name): # noqa
    task = ExportTask.objects.get(run__uid=run_uid, name=task_name)
    task.status = 'RUNNING'
    task.started_at = timezone.now()
    task.save()
    LOG.debug('Updated task: {0} for run: {1}'.format(task_name, run_uid))


def report_finished_task(run_uid, task_name, results): # noqa
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
def run_task_remote(run_uid): # noqa
    run = ExportRun.objects.get(uid=run_uid)
    run.status = 'RUNNING'
    run.started_at = timezone.now()
    run.save()
    LOG.debug('Running ExportRun with id: {0}'.format(run_uid))
    job = run.job
    # export_tasks = job.export_formats

    # setup the staging directory
    stage_dir = os.path.join(settings.EXPORT_STAGING_ROOT, str(run_uid)) + '/'
    os.makedirs(stage_dir, 6600)

    aoi = GEOSGeometry(job.the_geom)
    try:
        feature_selection = job.feature_selection_object
    except Exception:
        feature_selection = FeatureSelection(SIMPLE)

    osm_xml = OSM_XML(aoi, os.path.join(stage_dir, "osm_xml.osm"))
    osm_pbf = OSM_PBF(
        os.path.join(stage_dir, "osm_xml.osm"),
        os.path.join(stage_dir, "osm_pbf.pbf")
    )
    geopackage = Geopackage(
        os.path.join(stage_dir, "osm_pbf.pbf"),
        os.path.join(stage_dir, "geopackage.gpkg"),
        os.path.join(stage_dir, "osmconf.ini"),
        feature_selection,
        aoi
    )
    kml = KML(
        os.path.join(stage_dir, "geopackage.gpkg"),
        os.path.join(stage_dir, "kml.kmz")
    )
    # shp = Shapefile(
    #     os.path.join(stage_dir, "geopackage.gpkg"),
    #     os.path.join(stage_dir, "shapefile.shp.zip")
    # )
    thematic_gpkg = ThematicGPKG(
        os.path.join(stage_dir, "geopackage.gpkg"),
        feature_selection,
        stage_dir
    )
    thematic_shp = ThematicSHP(
        os.path.join(stage_dir, "geopackage.gpkg"),
        stage_dir,
        feature_selection,
        aoi
    )

    for task in [osm_xml, osm_pbf, geopackage, kml, thematic_gpkg,
                 thematic_shp]:
        report_started_task(run_uid, task.name)
        task.run()
        report_finished_task(run_uid, task.name, task.results)

    for task in [osm_xml, osm_pbf, geopackage, kml, thematic_gpkg,
                 thematic_shp]:
        run_dir = os.path.join(settings.EXPORT_DOWNLOAD_ROOT, run_uid)
        if not os.path.exists(run_dir):
            os.makedirs(run_dir)
        for result in task.results:
            filename = os.path.basename(result)
            download_path = os.path.join(
                settings.EXPORT_DOWNLOAD_ROOT, run_uid, filename)
            shutil.copy(result, download_path)

    run.status = 'COMPLETED'
    run.finished_at = timezone.now()
    run.save()
    LOG.debug('Finished ExportRun with id: {0}'.format(run_uid))

    if HDXExportRegion.objects.filter(job_id=run.job_id).exists():
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
                    'url': settings.HOSTNAME + os.path.join(
                        settings.EXPORT_MEDIA_ROOT,
                        run_uid,
                        theme + '_' + geom_type + ".zip"
                    )
                })
            resources.append({
                'name': theme + ' geopackage',
                'format': 'zipped geopackage',
                'description': "Geopackage of " + theme,
                'url': settings.HOSTNAME + os.path.join(
                    settings.EXPORT_MEDIA_ROOT, run_uid, theme + ".gpkg")
            })
            export_set.datasets[theme].add_update_resources(resources)
        export_set.sync_datasets()

    # finalize the task
    # shutil.rmtree(stage_dir)
    # send mail

    # except Exception as exc:
    #    print exc
    #    client.captureException(
    #        extra={
    #            'run_uid': run_uid,
    #            'task': exc,
    #        }
    #    )
