# -*- coding: utf-8 -*-
from __future__ import absolute_import

import cPickle
import os
import shutil

from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import EmailMultiAlternatives
from django.db import DatabaseError
from django.template.loader import get_template
from django.utils import timezone
from raven import Client

from core.celery import app
from jobs.presets import TagParser
from utils import (
    garmin,
    kml,
    osmand,
    osmconf,
    osmparse,
    overpass,
    pbf,
    shp,
    thematic_gpkg,
    thematic_shp,
)

client = Client()

# Get an instance of a logger
logger = get_task_logger(__name__)

class ExportTask(object):
    """
    Abstract base class for export tasks.
    """

    # whether to abort the whole run if this task fails.
    abort_on_error = False
    disabled = False

    class Meta:
        abstract = True

    def on_success(self, output_url, run_uid, name):
        from tasks.models import ExportTask
        """
        Update the successfuly completed task as follows:

            1. update the time the task completed
            2. calculate the size of the output file
            3. calculate the download path of the export
            4. create the export download directory
            5. copy the export file to the download directory
            6. create the export task result
            7. update the export task status and save it
        """
        finished = timezone.now()
        task = ExportTask.objects.get(run__uid=run_uid, name=name)
        task.finished_at = finished
        task.status = 'SUCCESS'

        if output_url != '':
            stat = os.stat(output_url)
            parts = output_url.split('/')
            filename = parts[-1]
            run_uid = parts[-2]
            run_dir = os.path.join(settings.EXPORT_DOWNLOAD_ROOT, run_uid)
            download_path = os.path.join(settings.EXPORT_DOWNLOAD_ROOT, run_uid, filename)
            if not os.path.exists(run_dir):
                os.makedirs(run_dir)
            # don't copy raw overpass data
            if (self.name != 'overpass'):
                shutil.copy(output_url, download_path)
            # construct the download url
            task.filesize_bytes = stat.st_size
            task.filename = filename

        task.save()

    #TODO this is not used; should be changed to a global Celery exption handler
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """
        Update the failed task as follows:

            1. pull out the ExportTask
            2. update the task status and finish time
            3. create an export task exception
            4. save the export task with the task exception
            5. run ExportTaskErrorHandler if the run should be aborted
               - this is only for initial tasks on which subsequent export tasks depend
        """
        client.captureException(
            extra={
                'task_id': task_id,
                'task': exc,
                'args': args,
                'kwargs': kwargs
            }
        )
        from tasks.models import ExportTask, ExportRun
        logger.debug('Task name: {0} failed, {1}'.format(self.name, einfo))
        task = ExportTask.objects.get(celery_uid=task_id)
        task.status = 'FAILED'
        task.finished_at = timezone.now()
        task.save()
        exception = cPickle.dumps(einfo)
        if self.abort_on_error:
            run = ExportRun.objects.get(tasks__celery_uid=task_id)
            run.status = 'FAILED'
            run.finished_at = timezone.now()
            run.save()
            error_handler = ExportTaskErrorHandler()
            # run error handler
            stage_dir = kwargs['stage_dir']
            error_handler.si(run_uid=str(run.uid),
                             task_id=task_id, stage_dir=stage_dir).delay()

    def after_return(self, *args, **kwargs):
        #logger.debug('Task returned: {0}'.format(self.request))
        pass

    def update_task_state(self, run_uid, name):
        """
        Update the task state and celery task uid.
        Can use the celery uid for diagnostics.
        """
        started = timezone.now()
        from tasks.models import ExportTask
        task = ExportTask.objects.get(run__uid=run_uid, name=name)
        task.status = 'RUNNING'
        task.started_at = started
        task.save()
        logger.debug('Updated task: {0} with uid: {1}'.format(task.name, task.uid))


class OSMConfTask(ExportTask):
    """
    Task to create the ogr2ogr conf file.
    """
    abort_on_error = True
    name = 'osmconf'

    def run(self, run_uid=None, categories=None, stage_dir=None, job_name=None):
        self.update_task_state(run_uid,self.name)
        conf = osmconf.OSMConfig(categories, job_name=job_name)
        configfile = conf.create_osm_conf(stage_dir=stage_dir)
        self.on_success("",run_uid,self.name)


class OverpassQueryTask(ExportTask):
    """
    Class to run an overpass query.
    """
    abort_on_error = True
    name = 'overpass'

    def run(self, run_uid=None, stage_dir=None, job_name=None, filters=None, bbox=None):
        """
        Runs the query and returns the path to the filtered osm file.
        """
        self.update_task_state(run_uid,self.name)
        op = overpass.Overpass(
            bbox, stage_dir,job_name, filters=filters,
            url=settings.OVERPASS_API_URL,
            overpass_max_size=settings.OVERPASS_MAX_SIZE,
            timeout=settings.OVERPASS_TIMEOUT
        )
        op.run_query()  # run the query
        filtered_osm = op.filter()  # filter the results
        self.on_success("",run_uid,self.name)


class OSMToPBFConvertTask(ExportTask):
    """
    Task to convert osm to pbf format.
    Returns the path to the pbf file.
    """
    name = 'osmtopbf'
    abort_on_error = True

    def run(self, run_uid=None, stage_dir=None, job_name=None):
        self.update_task_state(run_uid,self.name)
        osm = '{0}.osm'.format(os.path.join(stage_dir, job_name))
        pbffile = '{0}.pbf'.format(os.path.join(stage_dir, job_name))
        o2p = pbf.OSMToPBF(osm=osm, pbffile=pbffile)
        pbffile = o2p.convert()
        self.on_success("",run_uid,self.name)


class OSMPrepSchemaTask(ExportTask):
    """
    Task to create the default GeoPackage schema.
    """
    name = 'prep'
    abort_on_error = True

    def run(self, run_uid=None, stage_dir=None, job_name=None):
        self.update_task_state(run_uid,self.name)
        osm = '{0}.pbf'.format(os.path.join(stage_dir, job_name))
        gpkg = '{0}.gpkg'.format(os.path.join(stage_dir, job_name))
        osmconf = '{0}.ini'.format(os.path.join(stage_dir, job_name))
        osmparser = osmparse.OSMParser(osm=osm, gpkg=gpkg, osmconf=osmconf)
        osmparser.create_geopackage()
        osmparser.create_default_schema_gpkg()
        #osmparser.update_zindexes()
        self.on_success(gpkg,run_uid,self.name)


def osm_create_styles_task(self, result={}, run_uid=None, stage_dir=None, job_name=None, provider_slug=None, bbox=None):
    """
    Task to create styles for osm.
    """
    self.update_task_state(run_uid,self.name)
    input_gpkg = parse_result(result, 'geopackage')

    gpkg_file = '{0}-{1}-{2}.gpkg'.format(job_name,
                                          provider_slug,
                                          timezone.now().strftime('%Y%m%d'))
    style_file = os.path.join(stage_dir, '{0}-osm-{1}.qgs'.format(job_name,
                                                                  timezone.now().strftime("%Y%m%d")))

    with open(style_file, 'w') as open_file:
        open_file.write(render_to_string('styles/Style.qgs', context={
            'gpkg_filename': os.path.basename(gpkg_file),
            'layer_id_prefix': '{0}-osm-{1}'.format(job_name,
                                                    timezone.now().strftime("%Y%m%d")),
            'layer_id_date_time': '{0}'.format(
                timezone.now().strftime("%Y%m%d%H%M%S%f")[
                    :-3]),
            'bbox': bbox}))

    self.on_success(style_file,run_uid,self.name)


class PbfExportTask(ExportTask):
    """
    Convert unfiltered Overpass output to PBF.
    Returns the path to the PBF file.
    """
    name = 'pbf'
    description = 'OSM PBF'


    def run(self, run_uid=None, stage_dir=None, job_name=None):
        self.update_task_state(run_uid,self.name)
        osm = os.path.join(stage_dir, 'query.osm')
        pbffile = '{0}-full.pbf'.format(os.path.join(stage_dir, job_name))
        o2p = pbf.OSMToPBF(osm=osm, pbffile=pbffile)
        pbffile = o2p.convert()
        self.on_success(pbffile,run_uid,self.name)


class ThematicGeoPackageExportTask(ExportTask):
    """
    Task to export thematic GeoPackage.
    """
    name = 'theme_gpkg'
    description = 'GeoPackage (Thematic Schema)'

    def run(self, run_uid=None, stage_dir=None, job_name=None):
        from tasks.models import ExportRun
        self.update_task_state(run_uid,self.name)
        run = ExportRun.objects.get(uid=run_uid)
        tags = run.job.categorised_tags
        gpkg = '{0}.gpkg'.format(os.path.join(stage_dir, job_name))
        t2s = thematic_gpkg.GPKGToThematicGPKG(
            gpkg=gpkg, tags=tags, job_name=job_name)
        t2s.generate_thematic_schema()
        out = t2s.convert()
        self.on_success(out,run_uid,self.name)


class ThematicLayersExportTask(ExportTask):
    """
    Task to export thematic shapefile.
    """
    name = 'thematic'
    description = 'Esri SHP (Thematic Schema)'

    def run(self, run_uid=None, stage_dir=None, job_name=None):
        from tasks.models import ExportRun
        self.update_task_state(run_uid,self.name)
        run = ExportRun.objects.get(uid=run_uid)
        tags = run.job.categorised_tags
        gpkg = '{0}.gpkg'.format(os.path.join(stage_dir, job_name))
        t2s = thematic_shp.ThematicGPKGToShp(
            gpkg=gpkg, tags=tags, job_name=job_name)
        t2s.generate_thematic_schema()
        out = t2s.convert()
        self.on_success(out,run_uid,self.name)


class ShpExportTask(ExportTask):
    """
    Class defining SHP export function.
    """
    name = 'shp'
    description = 'ESRI SHP (OSM Schema)'

    def run(self, run_uid=None, stage_dir=None, job_name=None):
        self.update_task_state(run_uid,self.name)
        gpkg = '{0}.gpkg'.format(os.path.join(stage_dir, job_name))
        out = shp.GPKGToShp(gpkg=gpkg).convert()
        self.on_success(out,run_uid,self.name)


class KmlExportTask(ExportTask):
    """
    Class defining KML export function.
    """
    name = 'kml'
    description = 'Google Earth KMZ'

    def run(self, run_uid=None, stage_dir=None, job_name=None):
        self.update_task_state(run_uid,self.name)
        gpkg = '{0}.gpkg'.format(os.path.join(stage_dir, job_name))
        kmlfile = '{0}.kml'.format(os.path.join(stage_dir, job_name))
        s2k = kml.GPKGToKml(gpkg=gpkg, kmlfile=kmlfile)
        out = s2k.convert()
        self.on_success(out,run_uid,self.name)


class ObfExportTask(ExportTask):
    """
    Class defining OBF export function.
    """
    name = 'obf'
    description = 'OSMAnd OBF'

    def run(self, run_uid=None, stage_dir=None, job_name=None):
        self.update_task_state(run_uid,self.name)
        pbffile = '{0}.pbf'.format(os.path.join(stage_dir, job_name))
        map_creator_dir = settings.OSMAND_MAP_CREATOR_DIR
        work_dir = os.path.join(stage_dir, 'osmand')
        o2o = osmand.OSMToOBF(
            pbffile=pbffile, work_dir=work_dir, map_creator_dir=map_creator_dir
        )
        out = o2o.convert()
        obffile = '{0}.obf'.format(os.path.join(stage_dir, job_name))
        shutil.move(out, obffile)
        shutil.rmtree(work_dir)
        self.on_success(obffile,run_uid,self.name)


class SqliteExportTask(ExportTask):
    """
    Class defining SQLITE export function.
    """
    name = 'sqlite'
    description = 'SQLite Database'
    disabled = True

    def run(self, run_uid=None, stage_dir=None, job_name=None):
        self.update_task_state(run_uid,self.name)
        # sqlite already generated by OSMPrepSchema so just return path.
        sqlite = '{0}.sqlite'.format(os.path.join(stage_dir, job_name))
        self.on_success(sqlite,run_uid,self.name)


class GeoPackageExportTask(ExportTask):
    """
    Class defining GeoPackage export function.
    """
    name = 'geopackage'
    description = 'GeoPackage (OSM Schema)'

    def run(self, run_uid=None, stage_dir=None, job_name=None):
        self.update_task_state(run_uid,self.name)
        # gpkg already generated by OSMPrepSchema so just return path.
        gpkg = '{0}.gpkg'.format(os.path.join(stage_dir, job_name))
        self.on_success(gpkg,run_uid,self.name)


class GarminExportTask(ExportTask):
    """
    Class defining GARMIN export function.
    """
    name = 'garmin'
    description = 'Garmin Map'

    def run(self, run_uid=None, stage_dir=None, job_name=None):
        self.update_task_state(run_uid,self.name)
        work_dir = os.path.join(stage_dir, 'garmin')
        config = settings.GARMIN_CONFIG  # get path to garmin config
        pbffile = '{0}.pbf'.format(os.path.join(stage_dir, job_name))
        o2i = garmin.OSMToIMG(
            pbffile=pbffile, work_dir=work_dir,
            config=config, debug=False
        )
        o2i.run_splitter()
        out = o2i.run_mkgmap()
        imgfile = '{0}_garmin.zip'.format(os.path.join(stage_dir, job_name))
        shutil.move(out, imgfile)
        shutil.rmtree(work_dir)
        self.on_success(imgfile,run_uid,self.name)


class GeneratePresetTask(ExportTask):
    """
    Generates a JOSM Preset from the exports selected features.
    """
    name = 'preset'

    def run(self, run_uid=None, stage_dir=None, job_name=None):
        from tasks.models import ExportRun
        from jobs.models import ExportConfig
        self.update_task_state(run_uid,self.name)
        run = ExportRun.objects.get(uid=run_uid)
        job = run.job
        user = job.user
        feature_save = job.feature_save
        feature_pub = job.feature_pub
        # check if we should create a josm preset
        if feature_save or feature_pub:
            tags = job.tags.all()
            tag_parser = TagParser(tags=tags)
            xml = tag_parser.parse_tags()
            preset_file = ContentFile(xml)
            name = job.name
            filename = job_name + '_preset.xml'
            content_type = 'application/xml'
            config = ExportConfig.objects.create(
                name=name, filename=filename,
                config_type='PRESET', content_type=content_type,
                user=user, published=feature_pub
            )
            config.upload.save(filename, preset_file)

            output_path = config.upload.path
            job.config = config
            job.save()
            self.on_success(output_path,run_uid,self.name)


class FinalizeRunTask(object):
    """
    Finalizes export run.

    Cleans up staging directory.
    Updates run with finish time.
    Emails user notification.
    """

    def run(self, run_uid=None, stage_dir=None):
        logger.debug('Finalizing {0}'.format(run_uid))
        from tasks.models import ExportRun
        run = ExportRun.objects.get(uid=run_uid)
        run.status = 'COMPLETED'
        tasks = run.tasks.all()
        # mark run as incomplete if any tasks fail
        for task in tasks:
            if task.status == 'FAILED':
                run.status = 'INCOMPLETE'
        finished = timezone.now()
        run.finished_at = finished
        run.save()
        try:
            shutil.rmtree(stage_dir)
        except IOError:
            logger.error(
                'Error removing {0} during export finalize'.format(stage_dir))

        # send notification email to user
        hostname = settings.HOSTNAME
        url = 'http://{0}/exports/{1}'.format(hostname, run.job.uid)
        addr = run.user.email
        subject = "Your HOT Export is ready"
        to = [addr]
        from_email = 'HOT Exports <exports@hotosm.org>'
        ctx = {
            'url': url,
            'status': run.status
        }
        text = get_template('email/email.txt').render(ctx)
        html = get_template('email/email.html').render(ctx)
        msg = EmailMultiAlternatives(
            subject, text, to=to, from_email=from_email)
        msg.attach_alternative(html, "text/html")
        #msg.send()


FORMAT_NAMES = {}
for cls in [PbfExportTask,ThematicGeoPackageExportTask,
            ThematicLayersExportTask,ShpExportTask,
            KmlExportTask, ObfExportTask,SqliteExportTask,
            GeoPackageExportTask,GarminExportTask]:
    FORMAT_NAMES[cls.name] = cls
