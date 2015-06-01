import logging
import sys
import importlib
from hot_exports import settings
from jobs.models import Job

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
    export_registry = settings.EXPORT_TASKS
    
    def run_task(self, job_uid=None):
        logger.debug('Running Job with id: {0}'.format(job_uid))
        job = Job.objects.get(uid=job_uid)
        formats = [format.slug for format in job.formats.all()]
        # pick the export task based on the format..
        for format in formats:
            try:
                # see settings.EXPORT_TASKS for configuration
                task_fq_name = self.export_registry[format]
                
                """
                Instantiate the required class.
                """
                parts = task_fq_name.split('.')
                module_name, class_name = '.'.join(parts[:-1]), parts[-1]
                module = importlib.import_module(module_name)
                ExportTask = getattr(module, class_name)
                export_task = ExportTask()
                result = export_task.delay(job_uid=job_uid)
                job.status = result.state
                job.save()
            except KeyError as e:
                logger.debug(e)
                #TODO: how to report errors here?


class OSMUpdateTaskRunner(TaskRunner):
    pass
