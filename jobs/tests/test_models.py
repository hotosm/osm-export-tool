import logging
import sys
import uuid
from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from jobs.models import ExportTask, Job, ExportFormat

logger = logging.getLogger(__name__)
    

class TestExportTask(TestCase):
    """
    Test cases for ExportTask model
    """
    def setUp(self,):
        formats = ExportFormat.objects.all()
        user = User.objects.create(username='demo', email='demo@demo.com', password='demo')
        Job.objects.create(name='TestJob', description='Test description', user=user)
        job = Job.objects.all()[0]
        logger.debug('Job uid: {0}'.format(job.uid))
        # add the formats to the job
        job.formats = formats
        job.save()

    def test_create_export_task(self,):
        """
        Make sure task gets created correctly
        """
        job = Job.objects.all()[0]
        uid = uuid.uuid4()
        task = ExportTask.objects.create(job=job, uid=uid)
        saved_task = ExportTask.objects.get(uid=uid)
        self.assertEqual(task, saved_task)

    def test_export_task_uid(self,):
        """
        Make sure uid gets saved correctly
        """
        job = Job.objects.all()[0]
        uid = uuid.uuid4() # comes from celery task uid
        task = ExportTask.objects.create(job=job, uid=uid)
        logger.debug('UUID: {0}'.format(task.uid))
        self.assertEqual(uid, task.uid)
        

class TestJob(TestCase):
    """
    Test cases for Job model
    """
    def setUp(self,):
        self.formats = ExportFormat.objects.all() #pre-loaded by 'insert_export_formats' migration
        self.user = User.objects.create(username='demo', email='demo@demo.com', password='demo')
        self.job = Job.objects.create(name='TestJob', description='Test description', user=self.user)
        self.uid = self.job.uid
        # add the formats to the job
        self.job.formats = self.formats
        self.job.save()
        
    
    def test_job_creation(self, ):
        saved_job = Job.objects.all()[0]
        self.assertEqual(self.job, saved_job)
        self.assertEquals(self.uid, saved_job.uid)
        self.assertIsNotNone(saved_job.created_at)
        self.assertIsNotNone(saved_job.updated_at)
        self.assertEquals('', saved_job.status)
        saved_formats = saved_job.formats.all()
        self.assertIsNotNone(saved_formats)
        self.assertItemsEqual(saved_formats, self.formats)
    
    

