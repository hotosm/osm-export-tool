import logging
import json
import uuid
import os
from django.test import TestCase
from django.contrib.auth.models import User
from mock import Mock, patch, PropertyMock
from unittest import skip
from ..task_runners import ExportTaskRunner
from jobs.models import ExportFormat, Job
from django.contrib.gis.geos import GEOSGeometry, Polygon
from celery.datastructures import ExceptionInfo

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
        self.uid = str(self.job.uid)
    
    @patch('tasks.task_runners.chord')
    @patch('tasks.export_tasks.ShpExportTask')
    def test_run_task(self, mock_shp, mock_chord):
        format = ExportFormat.objects.get(slug='shp')
        celery_uid = str(uuid.uuid4())
        # shp export task mock
        export_task = mock_shp.return_value
        export_task.run.return_value = Mock(state='PENDING', id=celery_uid)
        type(export_task).name = PropertyMock(return_value='Shapefile Export')
        # celery chord mock
        celery_chord = mock_chord.return_value
        celery_chord.delay.return_value = Mock()
        self.job.formats.add(format)
        runner = ExportTaskRunner()
        runner.run_task(job_uid=self.uid)
        run = self.job.runs.all()[0]
        self.assertIsNotNone(run)
        # assert delay method called on mock chord..
        celery_chord.delay.assert_called_once()
        tasks = run.tasks.all()
        self.assertIsNotNone(tasks)
        self.assertEquals(5, len(tasks)) # 4 initial tasks + 1 shape export task
        self.assertFalse(hasattr(tasks[0], 'result')) # no result yet..    
