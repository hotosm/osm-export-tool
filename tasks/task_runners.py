# -*- coding: utf-8 -*-
import importlib
import logging
import os
import re
from datetime import datetime, timedelta

from django.conf import settings
from django.db import DatabaseError

from celery import chain, chord, group

from jobs.models import Job
from tasks.models import ExportRun, ExportTask

from .export_tasks import (
    FinalizeRunTask,
    GeneratePresetTask,
    OSMConfTask,
    OSMPrepSchemaTask,
    OSMToPBFConvertTask,
    OverpassQueryTask,
    osm_create_styles_task,
)

# Get an instance of a logger
LOG = logging.getLogger(__name__)

class ExportTaskRunner(object):
    """
    Runs HOT Export Tasks
    """
    def run_task(self, job_uid=None, user=None):
        """
        Run export tasks.

        Args:
            job_uid: the uid of the job to run.

        Return:
            the ExportRun instance.
        """
        run_uid = ''
        LOG.debug('Running Job with id: {0}'.format(job_uid))
        # pull the job from the database
        job = Job.objects.get(uid=job_uid)
        job_name = self.normalize_job_name(job.name)

        # build a list of celery tasks based on the export formats..
        export_tasks = [settings.EXPORT_FORMATS[format] for format in job.export_formats]

        assert len(export_tasks) > 0
        # add the new run
        if not user:
            user = job.user
        # add the export run to the database
        run = ExportRun.objects.create(job=job, user=user, status='SUBMITTED')  # persist the run
        run.save()
        run_uid = str(run.uid)
        LOG.debug('Saved run with id: {0}'.format(run_uid))

        # setup the staging directory
        stage_dir = os.path.join(settings.EXPORT_STAGING_ROOT, str(run_uid)) + '/'
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

        # save initial tasks to the db with 'PENDING' state..
        for initial_task in [conf, query, pbfconvert, prep_schema]:
            ExportTask.objects.create(run=run,
                                    status='PENDING', name=initial_task.name)
            LOG.debug('Saved task: {0}'.format(initial_task.name))
        # save the rest of the ExportFormat tasks.
        for export_task in export_tasks:
            ExportTask.objects.create(run=run,
                                      status='PENDING', name=export_task['name'])
            LOG.debug('Saved task: {0}'.format(export_task['name']))
        # check if we need to generate a preset file from Job feature selections
        if job.feature_save or job.feature_pub:
            # run GeneratePresetTask
            preset_task = GeneratePresetTask()
            ExportTask.objects.create(run=run,
                                          status='PENDING', name=preset_task.name)
            LOG.debug('Saved task: {0}'.format(preset_task.name))
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
            task['task'].si(run_uid=run_uid, stage_dir=stage_dir, job_name=job_name) for task in export_tasks
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
        ).apply_async()

        return run

    def normalize_job_name(self, name):
        # Remove all non-word characters
        s = re.sub(r"[^\w\s]", '', name)
        # Replace all whitespace with a single underscore
        s = re.sub(r"\s+", '_', s)
        return s.lower()
