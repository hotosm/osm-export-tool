#from __future__ import absolute_import

import logging
import time
import sys
import cPickle
from hot_exports import settings
from celery import app, shared_task, Task
from celery.registry import tasks
from celery.contrib.methods import task
from celery.utils.log import get_task_logger
from django.utils import timezone
from django.db import transaction, DatabaseError

from utils import overpass, osmconf, osmparse, pbf, shp, kml

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
        logger.debug('In success... Task name: {0}'.format(self.name))
        finished = timezone.now()
        result = retval['result']
        task = ExportTask.objects.get(uid=task_id)
        task.finished_at = finished
        task.status = 'SUCCESS'
        task.save()
        result = ExportTaskResult.objects.create(task=task, output_url=result)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        from tasks.models import ExportTask, ExportTaskException
        logger.debug('Task name: {0} failed, {1}'.format(self.name, einfo))
        task = ExportTask.objects.get(uid=task_id)
        task.status = 'FAILURE'
        task.finished_at = timezone.now()
        task.save()
        exception = cPickle.dumps(einfo)
        ExportTaskException.objects.create(task=task, exception=exception)

    def after_return(self, *args, **kwargs):
        logger.debug('Task returned: {0}'.format(self.request))
        
    def persist_task(self, run_uid=None):
        """
        Save the task to the database.
        """
        from tasks.models import ExportRun, ExportTask
        logger.debug('In persist task. Run uid: {0}'.format(run_uid))   
        celery_uid = self.request.id
        task_name = self.name
        try:
            run = ExportRun.objects.get(uid=run_uid)
            ExportTask.objects.create(run=run, uid=celery_uid,
                                      status='PENDING', name=task_name) # persist task with run and celery uid
            logger.debug('Saved task: {0} with uid: {1}'.format(task_name, celery_uid))
        except DatabaseError as e:
            logger.error('Persist task throws: {0}'.format(e))
            raise e


class OverpassQueryTask(ExportTask):
    """
    Class to run an overpass query.
    """
    name = 'OverpassQuery'
    
    def run(self, run_uid=None, stage_dir=None, bbox=None):
        """
        Runs the query and returns the path to the generated osm file.
        """
        self.persist_task(run_uid=run_uid)
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
        self.persist_task(run_uid=run_uid)
        osm = stage_dir + 'query.osm'
        pbffile = stage_dir + 'query.pbf'
        o2p = pbf.OSMToPBF(osm=osm, pbffile=pbffile)
        pbffile = o2p.convert()
        return {'result': pbffile}
    
    
class OSMConfTask(ExportTask):
    """
    Task to create the ogr conf file.
    """
    name = 'OSMConf'
    
    def run(self, run_uid=None, job_uid=None, categories=None, stage_dir=None):
        self.persist_task(run_uid=run_uid)
        conf = osmconf.OSMConfig(categories)
        configfile = conf.create_osm_conf(stage_dir=stage_dir)
        return {'result': configfile}

    
class OSMPrepSchemaTask(ExportTask):
    """
    Task to create the default sqlite schema.
    """
    name = 'OSMSchema'
    
    def run(self, run_uid=None, stage_dir=None):
        self.persist_task(run_uid=run_uid)
        osm = stage_dir + 'query.pbf'
        sqlite = stage_dir + 'query.sqlite'
        osmconf = stage_dir + 'osmconf.ini'
        osmparser = osmparse.OSMParser(osm=osm, sqlite=sqlite, osmconf=osmconf)
        return {'result': sqlite}
 

class ShpExportTask(ExportTask):
    """
    Class defining SHP export function.
    """
    name = 'Shapefile Export'
    
    def run(self, run_uid=None, stage_dir=None):
        self.persist_task(run_uid=run_uid)
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
        self.persist_task(run_uid=run_uid)
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
    
    def run(self, run_uid=None):
       
       # dummy task for now..
       # logic for SHP export goes here..
       time.sleep(10)
       return {'result': 'http://testserver/some/download/file.zip'}


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


class PgdumpExportTask(ExportTask):
    """
    Class defining PGDUMP export function.
    """
    
    name = 'PGDUMP Export'
    
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
    
    def run(self, run_uid=None):
       
       # dummy task for now..
       # logic for SHP export goes here..
       time.sleep(10)
       return {'result': 'http://testserver/some/download/file.zip'}



