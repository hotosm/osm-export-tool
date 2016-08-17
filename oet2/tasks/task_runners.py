# -*- coding: utf-8 -*-
import importlib
import logging
import os
import re
from datetime import datetime, timedelta

from django.conf import settings
from django.db import DatabaseError

from celery import chain, chord, group

from oet2.jobs.models import Job
from oet2.tasks.models import ExportRun, ExportTask

from .export_tasks import (
    FinalizeRunTask, GeneratePresetTask, OSMConfTask, OSMPrepSchemaTask,
    OSMToPBFConvertTask, OverpassQueryTask
)

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

    def run_task(self, job_uid=None, user=None):
        """
        Run export tasks.

        Args:
            job_uid: the uid of the job to run.

        Return:
            the ExportRun instance.
        """
        run_uid = ''
        logger.debug('Running Job with id: {0}'.format(job_uid))
        # pull the job from the database
        job = Job.objects.get(uid=job_uid)
        job_name = self.normalize_job_name(job.name)
        # get the formats to export
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
                # get the number of existing runs for this job
                run_count = job.runs.count()
                if run_count > 0:
                    while run_count > max_runs - 1:
                        # delete the earliest runs
                        job.runs.earliest(field_name='started_at').delete()  # delete earliest
                        run_count -= 1
                # add the new run
                if not user:
                    user = job.user
                # add the export run to the database
                run = ExportRun.objects.create(job=job, user=user, status='SUBMITTED')  # persist the run
                run.save()
                run_uid = str(run.uid)
                logger.debug('Saved run with id: {0}'.format(run_uid))
            except DatabaseError as e:
                logger.error('Error saving export run: {0}'.format(e))
                raise e

            # setup the staging directory
            stage_dir = settings.EXPORT_STAGING_ROOT + str(run_uid) + '/'
            os.makedirs(stage_dir, 6600)

            # pull out the tags to create the conf file
            categories = job.categorised_tags  # dict of points/lines/polygons
            bbox = job.overpass_extents  # extents of job in order required by overpass

            """
            Set up the initial tasks:
                1. Create the ogr2ogr config file for converting pbf to sqlite.
                2. Create the Overpass Query task which pulls raw data from overpass and filters it.
                3. Convert raw osm to compressed pbf.
                4. Create the default sqlite schema file using ogr2ogr config file created at step 1.
            """
            conf = OSMConfTask()
            query = OverpassQueryTask()
            pbfconvert = OSMToPBFConvertTask()
            prep_schema = OSMPrepSchemaTask()

            # check for transform and/or translate configurations
            """
            Not implemented for now.

            transform = job.configs.filter(config_type='TRANSFORM')
            translate = job.configs.filter(config_type='TRANSLATION')
            """

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
                if export_task.name == 'Garmin Export':
                    # add the region name to the Garmin export
                    export_task.region = job.region.name
                try:
                    ExportTask.objects.create(run=run,
                                              status='PENDING', name=export_task.name)
                    logger.debug('Saved task: {0}'.format(export_task.name))
                except DatabaseError as e:
                    logger.error('Saving task {0} threw: {1}'.format(export_task.name, e))
                    raise e
            # check if we need to generate a preset file from Job feature selections
            if job.feature_save or job.feature_pub:
                # run GeneratePresetTask
                preset_task = GeneratePresetTask()
                ExportTask.objects.create(run=run,
                                              status='PENDING', name=preset_task.name)
                logger.debug('Saved task: {0}'.format(preset_task.name))
                # add to export tasks
                export_tasks.append(preset_task)

            """
            Create a celery chain which runs the initial conf and query tasks (initial_tasks),
            followed by a chain of pbfconvert and prep_schema (schema_tasks).
            The export format tasks (format_tasks) are then run in parallel, followed
            by the finalize_task at the end to clean up staging dirs, update run status, email user etc..
            """
            initial_tasks = chain(
                    conf.si(categories=categories, stage_dir=stage_dir, run_uid=run_uid, job_name=job_name) |
                    query.si(stage_dir=stage_dir, job_name=job_name, bbox=bbox, run_uid=run_uid, filters=job.filters)
            )

            schema_tasks = chain(
                    pbfconvert.si(stage_dir=stage_dir, job_name=job_name, run_uid=run_uid) |
                    prep_schema.si(stage_dir=stage_dir, job_name=job_name, run_uid=run_uid)
            )

            format_tasks = group(
                task.si(run_uid=run_uid, stage_dir=stage_dir, job_name=job_name) for task in export_tasks
            )

            finalize_task = FinalizeRunTask()

            """
            If header tasks fail, errors will not propagate to the finalize_task.
            This means that the finalize_task will always be called, and will update the
            overall run status.
            """
            chain(
                    chain(initial_tasks, schema_tasks),
                    chord(header=format_tasks,
                        body=finalize_task.si(stage_dir=stage_dir, run_uid=run_uid))
            ).apply_async(expires=datetime.now() + timedelta(days=1))  # tasks expire after one day.

            return run

        else:
            return False

    def normalize_job_name(self, name):
        # Remove all non-word characters
        s = re.sub(r"[^\w\s]", '', name)
        # Replace all whitespace with a single underscore
        s = re.sub(r"\s+", '_', s)
        return s.lower()


def error_handler(task_id=None):
    logger.debug('In error handler %s' % task_id)
