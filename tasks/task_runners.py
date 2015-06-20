import logging
import sys
import os
import importlib
from hot_exports import settings
from jobs.models import Job
from tasks.models import ExportRun, ExportTask, ExportTaskResult
from jobs.presets import PresetParser
from celery import chain, group, chord
from .export_tasks import (OSMConfTask, OverpassQueryTask,
                           OSMPrepSchemaTask, OSMToPBFConvertTask)
from django.db import transaction, DatabaseError
import pdb

# Get an instance of a logger
logger = logging.getLogger(__name__)


class TaskRunner(object):
    """
    Abstract base class for running tasks
    """
    class Meta:
        abstract = True
        
    def run_task(self, *args, **kwargs):
        raise NotImplementedError('Override in subclass.')
       

class ExportTaskRunner(TaskRunner):
    """
    Runs HOT Export Tasks
    """
    export_task_registry = settings.EXPORT_TASKS
    
    def run_task(self, job_uid=None):
        #pdb.set_trace()
        logger.debug('Running Job with id: {0}'.format(job_uid))
        job = Job.objects.get(uid=job_uid)
        formats = [format.slug for format in job.formats.all()]
        logger.debug(formats)
        tasks = []
        # build a list of celery tasks based on the export formats..
        for format in formats:
            try:
                # see settings.EXPORT_TASKS for configuration
                task_fq_name = self.export_task_registry[format]
                # instantiate the required class.
                parts = task_fq_name.split('.')
                module_path, class_name = '.'.join(parts[:-1]), parts[-1]
                module = importlib.import_module(module_path)
                CeleryExportTask = getattr(module, class_name)
                export_task = CeleryExportTask()
                logger.debug(export_task.name)
                tasks.append(export_task)
            except KeyError as e:
                logger.debug(e)
            except ImportError as e:
                msg = 'Error importing export task: {0}'.format(e)
                logger.debug(msg)
        # run the tasks 
        if len(tasks) > 0:
            run_uid = None
            try:
                run = ExportRun.objects.create(job=job) # persist the run
                run.save()
                run_uid = str(run.uid)
                logger.debug('Saved run with id: {0}'.format(run_uid))
            except DatabaseError as e:
                logger.error('Error saving export run: {0}'.format(e))
                raise e
            
            # setup the staging directory
            stage_dir = settings.EXPORT_STAGING_ROOT + str(job_uid) + '/'
            os.makedirs(stage_dir, 6600)
            
            # pull out the tags to create the conf file
            categories = job.categorised_tags # dict of points/lines/polygons
            bbox = job.overpass_extents # extents of job in order required by overpass
            # setup the initial tasks
            conf = OSMConfTask()
            query = OverpassQueryTask()
            pbfconvert = OSMToPBFConvertTask()
            prep_schema = OSMPrepSchemaTask()
            for task in tasks:
                logger.debug(task.name)
            
            """
                Create a celery chord which runs the conf and query tasks in parallel,
                followed by a chain of pbfconvert and prep_schema
                which run sequentially when the others have completed.
            """
            initial_tasks = group(
                    conf.si(categories=categories, stage_dir=stage_dir, run_uid=run_uid),
                    query.si(stage_dir=stage_dir, bbox=bbox, run_uid=run_uid)
            )
            format_tasks = group(
                [task.si(run_uid=run_uid, stage_dir=stage_dir) for task in tasks]
            )
            schema_tasks = chain(
                    pbfconvert.si(stage_dir=stage_dir, run_uid=run_uid) | 
                    prep_schema.si(stage_dir=stage_dir, run_uid=run_uid) |
                    format_tasks
            )
            result = chord(
                header=initial_tasks,
                body=schema_tasks
            ).delay()
            
            return True
        else:
            return False


class OSMUpdateTaskRunner(TaskRunner):
    pass
