import logging
import sys
import os
import importlib
from datetime import datetime, timedelta
from hot_exports import settings
from jobs.models import Job
from tasks.models import ExportRun, ExportTask, ExportTaskResult
from jobs.presets import PresetParser
from celery import chain, group, chord
from .export_tasks import (OSMConfTask, OverpassQueryTask,
                           OSMPrepSchemaTask, OSMToPBFConvertTask,
                           FinalizeRunTask)
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
        run_uid = ''
        logger.debug('Running Job with id: {0}'.format(job_uid))
        job = Job.objects.get(uid=job_uid)
        formats = [format.slug for format in job.formats.all()]
        export_tasks = []
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
                export_tasks.append(export_task)
            except KeyError as e:
                logger.debug(e)
            except ImportError as e:
                msg = 'Error importing export task: {0}'.format(e)
                logger.debug(msg)
        # run the tasks 
        if len(export_tasks) > 0:
            # start the run
            run = None
            try:
                # enforce max runs
                max_runs = settings.EXPORT_MAX_RUNS
                run_count = job.runs.count()
                if run_count > 0:
                    while run_count > max_runs -1:
                        job.runs.earliest(field_name='started_at').delete() # delete earliest
                        run_count -= 1
                # save the run
                run = ExportRun.objects.create(job=job, status='SUBMITTED') # persist the run
                run.save()
                run_uid = str(run.uid)
                logger.debug('Saved run with id: {0}'.format(run_uid))
                max_runs = settings.EXPORT_MAX_RUNS
                run_count = job.runs.count()
                
            except DatabaseError as e:
                logger.error('Error saving export run: {0}'.format(e))
                raise e
            
            # setup the staging directory
            stage_dir = settings.EXPORT_STAGING_ROOT + str(run_uid) + '/'
            os.makedirs(stage_dir, 6600)
            
            # pull out the tags to create the conf file
            categories = job.categorised_tags # dict of points/lines/polygons
            bbox = job.overpass_extents # extents of job in order required by overpass
            # setup the initial tasks
            conf = OSMConfTask()
            query = OverpassQueryTask()
            pbfconvert = OSMToPBFConvertTask()
            prep_schema = OSMPrepSchemaTask()
            # save initial tasks to the db with 'PENDING' state..
            for initial_task in [conf, query, pbfconvert, prep_schema]:
                try:
                    ExportTask.objects.create(run=run,
                                              status='PENDING', name=initial_task.name)
                    logger.debug('Saved task: {0}'.format(initial_task.name))
                except DatabaseError as e:
                    logger.error('Saving task {0} threw: {1}'.format(initial_task.name, e))
                    raise e
            # save the rest of the ExportFormat tasks.
            for export_task in export_tasks:
                """
                    Set the region name on the Garmin Export task.
                    The region gets written to the exported '.img' file.
                    Could set additional params here in future if required.
                """
                if export_task.name == 'Garmin Export': export_task.region = job.region.name
                try:
                    ExportTask.objects.create(run=run,
                                              status='PENDING', name=export_task.name)
                    logger.debug('Saved task: {0}'.format(export_task.name))
                except DatabaseError as e:
                    logger.error('Saving task {0} threw: {1}'.format(export_task.name, e))
                    raise e
            
            """
                Create a celery chord which runs the initial conf and query tasks in parallel,
                followed by a chain of pbfconvert and prep_schema (schema_tasks)
                which run sequentially when the others have completed.
                The export format tasks (format_tasks) are then run in parallel afterwards.
                The Finalize task is run at the end to clean up staging dirs,
                update run status, email user etc..
            """
            initial_tasks = group(
                    conf.si(categories=categories, stage_dir=stage_dir, run_uid=run_uid),
                    query.si(stage_dir=stage_dir, bbox=bbox, run_uid=run_uid)
            )
            
            schema_tasks = chain(
                    pbfconvert.si(stage_dir=stage_dir, run_uid=run_uid) | 
                    prep_schema.si(stage_dir=stage_dir, run_uid=run_uid)
            )
            
            format_tasks = group(
                task.si(run_uid=run_uid, stage_dir=stage_dir) for task in export_tasks
            )
            
            finalize_task = FinalizeRunTask()
            
            chord(
                header=initial_tasks,
                body=schema_tasks | format_tasks |
                        finalize_task.si(stage_dir=stage_dir, run_uid=run_uid)
            ).apply_async(expires=datetime.now() + timedelta(days=1)) # tasks expire after one day.
            
            return run
        else:
            return False


class OSMUpdateTaskRunner(TaskRunner):
    pass
