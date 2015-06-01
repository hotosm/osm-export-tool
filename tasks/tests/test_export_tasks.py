# test cases for HOT Export Tasks
import logging
import json
import uuid
from django.test import TestCase
from django.contrib.auth.models import User
from mock import Mock, patch, PropertyMock
from ..task_runners import ExportTaskRunner
from jobs.models import ExportFormat, Job
from django.contrib.gis.geos import GEOSGeometry, Polygon

logger = logging.getLogger(__name__)

class TestExportTaskRunner(TestCase):
    
    def setUp(self,):
        self.user = User.objects.create(username='demo', email='demo@demo.com', password='demo')
        bbox = Polygon.from_bbox((-7.96, 22.6, -8.14, 27.12))
        the_geom = GEOSGeometry(bbox, srid=4326)
        self.job = Job.objects.create(name='TestJob',
                                 description='Test description', user=self.user,
                                 the_geom=the_geom)
        self.uid = str(self.job.uid)
    
    @patch('tasks.export_tasks.ShpExportTask')
    def test_run_task(self, mock):
        format = ExportFormat.objects.get(slug='shp')
        self.job.formats.add(format)
        celery_uid = str(uuid.uuid4())
        export_task = mock.return_value
        export_task.delay.return_value = Mock(state='PENDING', id=celery_uid)
        runner = ExportTaskRunner()
        runner.run_task(job_uid=self.uid)
        export_task.delay.assert_called_once_with(job_uid=self.uid)
        export_task.delay.return_value.assert_called('state')
        export_task.delay.return_value.assert_called('id')
        
        run = self.job.runs.all()[0]
        self.assertIsNotNone(run)
        tasks = run.tasks.all()
        self.assertIsNotNone(tasks)
        self.assertEquals(1, len(tasks)) # one shape export task
        self.assertFalse(hasattr(tasks[0], 'result')) # no result yet..
        job = Job.objects.get(uid=self.uid)
        self.assertEquals('PENDING', job.status)
         
    @patch('tasks.export_tasks.ShpExportTask')
    def test_run_shp_export_task(self, mock):
        format = ExportFormat.objects.get(slug='shp')
        self.job.formats.add(format)
        celery_uid = str(uuid.uuid4())
        export_task = mock.return_value
        export_task.delay.return_value = Mock(state='PENDING', id=celery_uid)
        runner = ExportTaskRunner()
        runner.run_task(job_uid=self.uid)
        export_task.delay.assert_called_with(job_uid=self.uid)
        export_task.delay.return_value.assert_called('state')
        export_task.delay.return_value.assert_called('id')
        job = Job.objects.get(uid=self.uid)
        self.assertEquals('PENDING', job.status)
    
    @patch('tasks.export_tasks.ObfExportTask')
    def test_run_obf_export_task(self, mock):
        format = ExportFormat.objects.get(slug='obf')
        self.job.formats.add(format)
        celery_uid = str(uuid.uuid4())
        export_task = mock.return_value
        export_task.delay.return_value = Mock(state='PENDING', id=celery_uid)
        runner = ExportTaskRunner()
        runner.run_task(job_uid=self.uid)
        export_task.delay.assert_called_with(job_uid=self.uid)
        export_task.delay.return_value.assert_called('state')
        job = Job.objects.get(uid=self.uid)
        self.assertEquals('PENDING', job.status)
        
    @patch('tasks.export_tasks.KmlExportTask')
    def test_run_kml_export_task(self, mock):
        format = ExportFormat.objects.get(slug='kml')
        self.job.formats.add(format)
        celery_uid = str(uuid.uuid4())
        export_task = mock.return_value
        export_task.delay.return_value = Mock(state='PENDING', id=celery_uid)
        runner = ExportTaskRunner()
        runner.run_task(job_uid=self.uid)
        export_task.delay.assert_called_with(job_uid=self.uid)
        export_task.delay.return_value.assert_called('state')
        export_task.delay.return_value.assert_called('id')
        job = Job.objects.get(uid=self.uid)
        self.assertEquals('PENDING', job.status)
    
    @patch('tasks.export_tasks.SqliteExportTask')
    def test_run_sqlite_export_task(self, mock):
        format = ExportFormat.objects.get(slug='sqlite')
        self.job.formats.add(format)
        celery_uid = str(uuid.uuid4())
        export_task = mock.return_value
        export_task.delay.return_value = Mock(state='PENDING', id=celery_uid)
        runner = ExportTaskRunner()
        runner.run_task(job_uid=self.uid)
        export_task.delay.assert_called_with(job_uid=self.uid)
        export_task.delay.return_value.assert_called('state')
        export_task.delay.return_value.assert_called('id')
        job = Job.objects.get(uid=self.uid)
        self.assertEquals('PENDING', job.status)
        
    @patch('tasks.export_tasks.GarminExportTask')
    def test_run_garmin_export_task(self, mock):
        format = ExportFormat.objects.get(slug='garmin')
        self.job.formats.add(format)
        celery_uid = str(uuid.uuid4())
        export_task = mock.return_value
        export_task.delay.return_value = Mock(state='PENDING', id=celery_uid)
        runner = ExportTaskRunner()
        runner.run_task(job_uid=self.uid)
        export_task.delay.assert_called_with(job_uid=self.uid)
        export_task.delay.return_value.assert_called('state')
        export_task.delay.return_value.assert_called('id')
        job = Job.objects.get(uid=self.uid)
        self.assertEquals('PENDING', job.status)
    
    @patch('tasks.export_tasks.PgdumpExportTask')
    def test_run_pgdump_export_task(self, mock):
        format = ExportFormat.objects.get(slug='pgdump')
        self.job.formats.add(format)
        celery_uid = str(uuid.uuid4())
        export_task = mock.return_value
        export_task.delay.return_value = Mock(state='PENDING', id=celery_uid)
        runner = ExportTaskRunner()
        runner.run_task(job_uid=self.uid)
        export_task.delay.assert_called_with(job_uid=self.uid)
        export_task.delay.return_value.assert_called('state')
        export_task.delay.return_value.assert_called('id')
        job = Job.objects.get(uid=self.uid)
        self.assertEquals('PENDING', job.status)
