# -*- coding: utf-8 -*-
import importlib
import logging
import os
import re
from datetime import datetime, timedelta

from django.conf import settings
from django.db import DatabaseError

from celery import shared_task

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
        job_name = normalize_job_name(job.name)

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
            preset_task = GeneratePresetTask()
            ExportTask.objects.create(run=run,
                                          status='PENDING', name=preset_task.name)
            LOG.debug('Saved task: {0}'.format(preset_task.name))
            # add to export tasks
            export_tasks.append(preset_task)

        run_task_remote.delay(run_uid)



def normalize_job_name(name):
    # Remove all non-word characters
    s = re.sub(r"[^\w\s]", '', name)
    # Replace all whitespace with a single underscore
    s = re.sub(r"\s+", '_', s)
    return s.lower()


@shared_task
def run_task_remote(run_uid):
    run = ExportRun.objects.get(uid=run_uid)
    LOG.debug('Running ExportRun with id: {0}'.format(run_uid))
    job = run.job
    job_name = normalize_job_name(job.name)
    export_tasks = [settings.EXPORT_FORMATS[format] for format in job.export_formats]

    conf = OSMConfTask()
    query = OverpassQueryTask()
    pbfconvert = OSMToPBFConvertTask()
    prep_schema = OSMPrepSchemaTask()

    # setup the staging directory
    stage_dir = os.path.join(settings.EXPORT_STAGING_ROOT, str(run_uid)) + '/'
    os.makedirs(stage_dir, 6600)

    # pull out the tags to create the conf file
    categories = job.categorised_tags  # dict of points/lines/polygons
    bbox = job.overpass_extents  # extents of job in order required by overpass

    conf.run(categories=categories, stage_dir=stage_dir, run_uid=run_uid, job_name=job_name)
    query.run(stage_dir=stage_dir, job_name=job_name, bbox=bbox, run_uid=run_uid, filters=job.filters)

    pbfconvert.run(stage_dir=stage_dir,job_name=job_name,run_uid=run_uid)
    prep_schema.run(stage_dir=stage_dir, job_name=job_name, run_uid=run_uid)

    for task in export_tasks:
        task['task']().run(run_uid=run_uid, stage_dir=stage_dir, job_name=job_name)

    # TODO this should run in the case of an exception
    finalize_task = FinalizeRunTask().run(run_uid=run_uid,stage_dir=stage_dir)

    return run
