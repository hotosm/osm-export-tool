import logging
import sys
import importlib
from hot_exports import settings
from jobs.models import Job
from tasks.models import ExportRun, ExportTask, ExportTaskResult

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
        logger.debug('Running Job with id: {0}'.format(job_uid))
        job = Job.objects.get(uid=job_uid)
        formats = [format.slug for format in job.formats.all()]
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
                tasks.append(export_task)
            except KeyError as e:
                logger.debug(e)
            except ImportError as e:
                msg = 'Could not import {0} as ExportTask. {1}'.format(e.__class__.__name__, e)
                logger.warn(msg)
        # run the tasks and persist audit info to db..
        if len(tasks) > 0:
            run = ExportRun.objects.create(job=job) # persist the run
            for task in tasks:
                result = task.delay(job_uid=job_uid) # add task to celery queue
                # update the job with the initial state..??? on Job or on Run?
                job.status = result.state
                job.save()
                celery_uid = result.id
                ExportTask.objects.create(run=run, uid=celery_uid) # persist task with run and celery uid
        else:
            # no tasks to run... do something here..
            pass


class OSMUpdateTaskRunner(TaskRunner):
    pass
