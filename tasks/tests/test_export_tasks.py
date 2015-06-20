# test cases for HOT Export Tasks
import logging
import json
import uuid
import sys
import cPickle
import traceback
import os
from django.test import TestCase
from django.contrib.auth.models import User
from mock import Mock, patch, PropertyMock
from unittest import skip
from ..task_runners import ExportTaskRunner
from jobs.models import ExportFormat, Job, Tag
from django.contrib.gis.geos import GEOSGeometry, Polygon
from tasks.export_tasks import ExportTask, ShpExportTask
from tasks.models import ExportRun, ExportTask, ExportTaskResult
from celery.datastructures import ExceptionInfo
from jobs.presets import PresetParser


logger = logging.getLogger(__name__)
  

class TestExportTaskRunner(TestCase):
    
    def setUp(self,):
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.user = User.objects.create(username='demo', email='demo@demo.com', password='demo')
        #bbox = Polygon.from_bbox((-7.96, 22.6, -8.14, 27.12))
        bbox = Polygon.from_bbox((-10.85,6.25,-10.62,6.40))
        the_geom = GEOSGeometry(bbox, srid=4326)
        self.job = Job.objects.create(name='TestJob',
                                 description='Test description', user=self.user,
                                 the_geom=the_geom)
        preset_parser = PresetParser(preset=self.path + '/files/hdm_presets.xml')
        tags = preset_parser.parse(merge_with_defaults=False)
        for key in tags:
            tag = Tag.objects.create(
                name = key,
                geom_types = tags[key]
            )
            self.job.tags.add(tag)
        self.uid = str(self.job.uid)
    
    @patch('tasks.export_tasks.ShpExportTask')
    def test_run_task(self, mock):
        format = ExportFormat.objects.get(slug='shp')
        self.job.formats.add(format)
        celery_uid = str(uuid.uuid4())
        export_task = mock.return_value
        export_task.delay.return_value = Mock(state='PENDING', id=celery_uid)
        type(export_task).name = PropertyMock(return_value='Shapefile Export')
        runner = ExportTaskRunner()
        runner.run_task(job_uid=self.uid)
        run = self.job.runs.all()[0]
        self.assertIsNotNone(run)
        export_task.delay.assert_called_once_with(run_uid=str(run.uid))
        export_task.delay.return_value.assert_called_once('state')
        export_task.delay.return_value.assert_called_once('id')
        
        tasks = run.tasks.all()
        self.assertIsNotNone(tasks)
        self.assertEquals(1, len(tasks)) # one shape export task
        self.assertFalse(hasattr(tasks[0], 'result')) # no result yet..
        job = Job.objects.get(uid=self.uid)
        
    
    def test_run_task_debug(self,):
        format = ExportFormat.objects.get(slug='shp')
        self.job.formats.add(format)
        runner = ExportTaskRunner()
        runner.run_task(job_uid=self.uid)
        run = self.job.runs.all()[0]
        self.assertIsNotNone(run)
        tasks = ExportTask.objects.filter(run__uid=run.uid)
        
        self.assertIsNotNone(tasks)
        self.assertEquals(4, len(tasks)) # one shape export task
        self.assertFalse(hasattr(tasks[0], 'result')) # no result yet..
        
         
    @patch('tasks.export_tasks.ShpExportTask')
    def test_run_shp_export_task(self, mock):
        format = ExportFormat.objects.get(slug='shp')
        self.job.formats.add(format)
        celery_uid = str(uuid.uuid4())
        export_task = mock.return_value
        export_task.delay.return_value = Mock(state='PENDING', id=celery_uid)
        type(export_task).name = PropertyMock(return_value='Shapefile Export')
        runner = ExportTaskRunner()
        runner.run_task(job_uid=self.uid)
        run = self.job.runs.all()[0]
        self.assertIsNotNone(run)
        export_task.delay.assert_called_with(run_uid=str(run.uid))
        export_task.delay.return_value.assert_called_once('state')
        export_task.delay.return_value.assert_called_once('id')
        job = Job.objects.get(uid=self.uid)
    
    @patch('tasks.export_tasks.ObfExportTask')
    def test_run_obf_export_task(self, mock):
        format = ExportFormat.objects.get(slug='obf')
        self.job.formats.add(format)
        celery_uid = str(uuid.uuid4())
        export_task = mock.return_value
        export_task.delay.return_value = Mock(state='PENDING', id=celery_uid)
        type(export_task).name = PropertyMock(return_value='OBF Export')
        runner = ExportTaskRunner()
        runner.run_task(job_uid=self.uid)
        run = self.job.runs.all()[0]
        self.assertIsNotNone(run)
        export_task.delay.assert_called_with(run_uid=str(run.uid))
        export_task.delay.return_value.assert_called_once('state')
        job = Job.objects.get(uid=self.uid)
        
    @patch('tasks.export_tasks.KmlExportTask')
    def test_run_kml_export_task(self, mock):
        format = ExportFormat.objects.get(slug='kml')
        self.job.formats.add(format)
        celery_uid = str(uuid.uuid4())
        export_task = mock.return_value
        export_task.delay.return_value = Mock(state='PENDING', id=celery_uid)
        type(export_task).name = PropertyMock(return_value='KML Export')
        runner = ExportTaskRunner()
        runner.run_task(job_uid=self.uid)
        run = self.job.runs.all()[0]
        self.assertIsNotNone(run)
        export_task.delay.assert_called_with(run_uid=str(run.uid))
        export_task.delay.return_value.assert_called_once('state')
        export_task.delay.return_value.assert_called_once('id')
        job = Job.objects.get(uid=self.uid)
    
    @patch('tasks.export_tasks.SqliteExportTask')
    def test_run_sqlite_export_task(self, mock):
        format = ExportFormat.objects.get(slug='sqlite')
        self.job.formats.add(format)
        celery_uid = str(uuid.uuid4())
        export_task = mock.return_value
        export_task.delay.return_value = Mock(state='PENDING', id=celery_uid)
        type(export_task).name = PropertyMock(return_value='SQLITE Export')
        runner = ExportTaskRunner()
        runner.run_task(job_uid=self.uid)
        run = self.job.runs.all()[0]
        self.assertIsNotNone(run)
        export_task.delay.assert_called_with(run_uid=str(run.uid))
        export_task.delay.return_value.assert_called_once('state')
        export_task.delay.return_value.assert_called_once('id')
        job = Job.objects.get(uid=self.uid)
        
    @patch('tasks.export_tasks.GarminExportTask')
    def test_run_garmin_export_task(self, mock):
        format = ExportFormat.objects.get(slug='garmin')
        self.job.formats.add(format)
        celery_uid = str(uuid.uuid4())
        export_task = mock.return_value
        export_task.delay.return_value = Mock(state='PENDING', id=celery_uid)
        type(export_task).name = PropertyMock(return_value='Garmin Export')
        runner = ExportTaskRunner()
        runner.run_task(job_uid=self.uid)
        run = self.job.runs.all()[0]
        self.assertIsNotNone(run)
        export_task.delay.assert_called_with(run_uid=str(run.uid))
        export_task.delay.return_value.assert_called_once('state')
        export_task.delay.return_value.assert_called_once('id')
        job = Job.objects.get(uid=self.uid)
    
    @patch('tasks.export_tasks.PgdumpExportTask')
    def test_run_pgdump_export_task(self, mock):
        format = ExportFormat.objects.get(slug='pgdump')
        self.job.formats.add(format)
        celery_uid = str(uuid.uuid4())
        export_task = mock.return_value
        export_task.delay.return_value = Mock(state='PENDING', id=celery_uid)
        type(export_task).name = PropertyMock(return_value='PGDUMP Export')
        runner = ExportTaskRunner()
        runner.run_task(job_uid=self.uid)
        run = self.job.runs.all()[0]
        self.assertIsNotNone(run)
        export_task.delay.assert_called_with(run_uid=str(run.uid))
        export_task.delay.return_value.assert_called_once('state')
        export_task.delay.return_value.assert_called_once('id')
        job = Job.objects.get(uid=self.uid)
    
    @patch('tasks.export_tasks.ShpExportTask')
    def test_task_on_success(self, mock):
        format = ExportFormat.objects.get(slug='shp')
        self.job.formats.add(format)
        celery_uid = str(uuid.uuid4())
        export_task = mock.return_value
        export_task.delay.return_value = Mock(state='PENDING', id=celery_uid)
        type(export_task).name = PropertyMock(return_value='Shapefile Export')
        runner = ExportTaskRunner()
        runner.run_task(job_uid=self.uid)
        run = self.job.runs.all()[0]
        self.assertIsNotNone(run)
        export_task.delay.assert_called_with(run_uid=str(run.uid))
        export_task.delay.return_value.assert_called_once('state')
        export_task.delay.return_value.assert_called_once('id')
        
        """
        Call the on_success method directly to test.
        Would be called by celery worker on successful completion of task.
        """
        shp_export_task = ShpExportTask()
        output_url = 'http://testserver/some/output/file.zip'
        shp_export_task.on_success(retval={'result': output_url}, task_id=celery_uid,
                                   args={}, kwargs={'job_uid':self.uid})
        task = ExportTask.objects.get(uid=celery_uid)
        self.assertIsNotNone(task)
        result = task.result
        self.assertIsNotNone(result)
        self.assertEqual(task, result.task)
        self.assertEquals('SUCCESS', task.status)
        self.assertEquals('Shapefile Export', task.name)
    
    @patch('tasks.export_tasks.ShpExportTask')
    def test_task_on_failure(self, mock):
        format = ExportFormat.objects.get(slug='shp')
        self.job.formats.add(format)
        celery_uid = str(uuid.uuid4())
        export_task = mock.return_value
        export_task.delay.return_value = Mock(state='PENDING', id=celery_uid)
        type(export_task).name = PropertyMock(return_value='Shapefile Export')
        runner = ExportTaskRunner()
        runner.run_task(job_uid=self.uid)
        run = self.job.runs.all()[0]
        self.assertIsNotNone(run)
        export_task.delay.assert_called_with(run_uid=str(run.uid))
        export_task.delay.return_value.assert_called_once('state')
        export_task.delay.return_value.assert_called_once('id')
        """
        Call the on_faillure method directly.
        Would be called by celery worker on failure of task.
        """
        shp_export_task = ShpExportTask()
        exc = None
        exc_info = None
        try:
            raise ValueError('some unexpected error')
        except ValueError as e:
            exc = e
            exc_info = sys.exc_info()
        einfo = ExceptionInfo(exc_info=exc_info)
        shp_export_task.on_failure(exc, task_id=celery_uid, einfo=einfo,
                                   args={}, kwargs={'job_uid':self.uid})
        task = ExportTask.objects.get(uid=celery_uid)
        self.assertIsNotNone(task)
        exception = task.exceptions.all()[0]
        exc_info = cPickle.loads(str(exception.exception)).exc_info
        error_type, msg, tb = exc_info[0], exc_info[1], exc_info[2]
        self.assertEquals(error_type, ValueError)
        self.assertEquals('some unexpected error', str(msg))
        #traceback.print_exception(error_type, msg, tb)
        
        
        
