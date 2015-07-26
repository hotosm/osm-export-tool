#from __future__ import absolute_import
import logging
import time
import sys
import cPickle
import shutil
import os
from hot_exports import settings
from celery import app, shared_task, Task
from celery.registry import tasks
from celery.contrib.methods import task
from celery.utils.log import get_task_logger
from django.utils import timezone
from django.db import transaction, DatabaseError
from django.template import Context
from django.template.loader import get_template
from django.core.mail import EmailMessage

from utils import (overpass, osmconf, osmparse,
                   pbf, shp, kml, osmand, garmin)

# Get an instance of a logger
logger = get_task_logger(__name__)


# ExportTask abstract base class and subclasses.

class ExportTask(Task):
    """
    Abstract base class for export tasks.
    """
    class Meta:
        abstract = True

    def on_success(self, retval, task_id, args, kwargs):
        from tasks.models import ExportTask, ExportTaskResult
        # update the task
        finished = timezone.now()
        task = ExportTask.objects.get(celery_uid=task_id)
        task.finished_at = finished
        # get the output
        output_url = retval['result']
        stat = os.stat(output_url)
        size = stat.st_size / 1024 / 1024.00
        # construct the download_path
        download_root = settings.EXPORT_DOWNLOAD_ROOT
        parts = output_url.split('/')
        filename = parts[-1]
        run_uid = parts[-2]
        run_dir = '{0}{1}'.format(download_root, run_uid)
        download_path = '{0}{1}/{2}'.format(download_root, run_uid, filename)
        try:
            if not os.path.exists(run_dir):
                os.makedirs(run_dir)
            shutil.copy(output_url, download_path)
        except IOError as e:
            logger.error('Error copying output file to: {0}'.format(download_path))
        # construct the download url
        download_media_root = settings.EXPORT_MEDIA_ROOT
        download_url = '{0}{1}/{2}'.format(download_media_root, run_uid, filename)
        # save the task and task result
        result = ExportTaskResult(
            task=task,
            filename=filename,
            size=size,
            download_url=download_url
        )
        result.save()
        task.status = 'SUCCESS'
        task.save()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        from tasks.models import ExportTask, ExportTaskException
        logger.debug('Task name: {0} failed, {1}'.format(self.name, einfo))
        task = ExportTask.objects.get(celery_uid=task_id)
        task.status = 'FAILURE'
        task.finished_at = timezone.now()
        task.save()
        exception = cPickle.dumps(einfo)
        ete = ExportTaskException(task=task, exception=exception)
        ete.save()

    def after_return(self, *args, **kwargs):
        logger.debug('Task returned: {0}'.format(self.request))
        
    def update_task_state(self, run_uid=None, name=None):
        """
        Update the task state and celery task uid.
        Can use the celery uid for diagnostics. 
        """
        started = timezone.now()
        from tasks.models import ExportRun, ExportTask 
        celery_uid = self.request.id
        try:
            task = ExportTask.objects.get(run__uid=run_uid, name=name)
            celery_uid = self.request.id
            task.celery_uid = celery_uid
            task.status = 'RUNNING'
            task.started_at = started
            task.save()
            logger.debug('Updated task: {0} with uid: {1}'.format(task.name, task.uid))
        except DatabaseError as e:
            logger.error('Updating task {0} state throws: {1}'.format(task.name, e))
            raise e


class OSMConfTask(ExportTask):
    """
    Task to create the ogr2ogr conf file.
    """
    name = 'OSMConf'
    
    def run(self, run_uid=None, job_uid=None, categories=None, stage_dir=None):
        self.update_task_state(run_uid=run_uid, name=self.name)
        conf = osmconf.OSMConfig(categories)
        configfile = conf.create_osm_conf(stage_dir=stage_dir)
        return {'result': configfile}
   

class OverpassQueryTask(ExportTask):
    """
    Class to run an overpass query.
    """
    name = 'OverpassQuery'
    
    def run(self, run_uid=None, stage_dir=None, bbox=None):
        """
        Runs the query and returns the path to the generated osm file.
        """
        self.update_task_state(run_uid=run_uid, name=self.name)
        osm = stage_dir + 'query.osm'
        op = overpass.Overpass(bbox=bbox, osm=osm)
        osmfile = op.run_query()
        return {'result': osmfile}


class OSMToPBFConvertTask(ExportTask):
    """
    Task to convert osm to pbf format.
    Returns the path to the pbf file.
    """
    name = 'OSM2PBF'
    
    def run(self, run_uid=None, stage_dir=None):
        self.update_task_state(run_uid=run_uid, name=self.name)
        osm = stage_dir + 'query.osm'
        pbffile = stage_dir + 'query.pbf'
        o2p = pbf.OSMToPBF(osm=osm, pbffile=pbffile)
        pbffile = o2p.convert()
        return {'result': pbffile}
    
 
class OSMPrepSchemaTask(ExportTask):
    """
    Task to create the default sqlite schema.
    """
    name = 'OSMSchema'
    
    def run(self, run_uid=None, stage_dir=None):
        self.update_task_state(run_uid=run_uid, name=self.name)
        osm = stage_dir + 'query.pbf'
        sqlite = stage_dir + 'query.sqlite'
        osmconf = stage_dir + 'osmconf.ini'
        osmparser = osmparse.OSMParser(osm=osm, sqlite=sqlite, osmconf=osmconf)
        osmparser.create_spatialite()
        osmparser.create_default_schema()
        osmparser.update_zindexes()
        return {'result': sqlite}
 

class ShpExportTask(ExportTask):
    """
    Class defining SHP export function.
    """
    name = 'Shapefile Export'
    
    def run(self, run_uid=None, stage_dir=None):
        self.update_task_state(run_uid=run_uid, name=self.name)
        sqlite = stage_dir + 'query.sqlite'
        shapefile = stage_dir + 'shp'
        s2s = shp.SQliteToShp(sqlite=sqlite, shapefile=shapefile)
        out = s2s.convert()
        return {'result': out}


class KmlExportTask(ExportTask):
    """
    Class defining KML export function.
    """
    name = 'KML Export'
    
    def run(self, run_uid=None, stage_dir=None):
        self.update_task_state(run_uid=run_uid, name=self.name)
        sqlite = stage_dir + 'query.sqlite'
        kmlfile = stage_dir + 'query.kml'
        s2k = kml.SQliteToKml(sqlite=sqlite, kmlfile=kmlfile)
        out = s2k.convert()
        return {'result': out}


class ObfExportTask(ExportTask):    
    """
    Class defining OBF export function.
    """
    name = 'OBF Export'
    
    def run(self, run_uid=None, stage_dir=None):
        self.update_task_state(run_uid=run_uid, name=self.name)
        pbffile = stage_dir + 'query.pbf'
        map_creator_dir = settings.OSMAND_MAP_CREATOR_DIR
        work_dir = stage_dir + 'osmand'
        o2o = osmand.OSMToOBF(
            pbffile=pbffile, work_dir=work_dir, map_creator_dir=map_creator_dir
        )
        out = o2o.convert()
        obffile = stage_dir + 'query.obf'
        shutil.move(out, obffile)
        shutil.rmtree(work_dir)
        return {'result': obffile}


class SqliteExportTask(ExportTask):
    """
    Class defining SQLITE export function.
    """
    
    name = 'SQLITE Export'
    
    def run(self, run_uid=None):
       
       # dummy task for now..
       # logic for SHP export goes here..
       time.sleep(10)
       return {'result': 'http://testserver/some/download/file.zip'}


class GarminExportTask(ExportTask):
    """
    Class defining GARMIN export function.
    """
    
    name = 'Garmin Export'
    _region = '' # set by the task_runner
    
    @property
    def region(self,):
        return self._region
    
    @region.setter
    def region(self, value):
        self._region = value
    
    def run(self, run_uid=None, stage_dir=None):
        self.update_task_state(run_uid=run_uid, name=self.name)
        work_dir = stage_dir + 'garmin'
        config = settings.GARMIN_CONFIG # get path to garmin config
        pbffile = stage_dir + 'query.pbf'
        o2i = garmin.OSMToIMG(
            pbffile=pbffile, work_dir=work_dir,
            config=config, region=None, debug=False
        )
        o2i.run_splitter()
        out = o2i.run_mkgmap()
        imgfile = stage_dir + 'garmin.zip'
        shutil.move(out, imgfile)
        shutil.rmtree(work_dir)
        return {'result': imgfile}


class FinalizeRunTask(Task):
    """
    Finalizes export run.
    Cleans up staging directory.
    Updates run with finish time.
    Emails user notification.
    """
    
    name = 'Finalize Export Run'
    
    def run(self, run_uid=None, stage_dir=None):
        from tasks.models import ExportRun
        finished = timezone.now()
        run =  ExportRun.objects.get(uid=run_uid)
        run.finished_at = finished
        run.status = 'COMPLETED'
        run.save()
        try:
            shutil.rmtree(stage_dir)
        except IOError as e:
            logger.error('Error removing {0} during export finalize'.format(stage_dir))
            
        # send notification email to user
        hostname = settings.HOSTNAME
        url = 'http://{0}/jobs/{1}'.format(hostname, run.job.uid)
        addr = run.job.user.email
        subject = "Your HOT Export is ready"
        to = [addr]
        from_email = 'exports@hotosm.org'
        ctx = {
            'url': url,
        }
        message = get_template('ui/email.html').render(Context(ctx))
        msg = EmailMessage(subject, message, to=to, from_email=from_email)
        msg.content_subtype = 'html'
        msg.send()