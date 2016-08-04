# -*- coding: utf-8 -*-
import logging
import os
import uuid

from mock import Mock, PropertyMock, patch

from django.contrib.auth.models import Group, User
from django.contrib.gis.geos import GEOSGeometry, Polygon
from django.test import TestCase

from oet2.jobs.models import ExportFormat, Job, Region

from ..task_runners import ExportTaskRunner

logger = logging.getLogger(__name__)


class TestExportTaskRunner(TestCase):

    def setUp(self,):
        self.path = os.path.dirname(os.path.realpath(__file__))
        Group.objects.create(name='TestDefaultExportExtentGroup')
        self.user = User.objects.create(username='demo', email='demo@demo.com', password='demo')
        # bbox = Polygon.from_bbox((-7.96, 22.6, -8.14, 27.12))
        bbox = Polygon.from_bbox((-10.85, 6.25, -10.62, 6.40))
        the_geom = GEOSGeometry(bbox, srid=4326)
        self.job = Job.objects.create(name='TestJob',
                                 description='Test description', user=self.user,
                                 the_geom=the_geom)
        self.region = Region.objects.get(name='Africa')
        self.job.region = self.region
        self.uid = str(self.job.uid)
        self.job.save()

    @patch('tasks.task_runners.chain')
    @patch('tasks.export_tasks.GarminExportTask')
    @patch('tasks.export_tasks.ShpExportTask')
    def test_run_task(self, mock_shp, mock_garmin, mock_chain):
        shp_task = ExportFormat.objects.get(slug='shp')
        garmin_task = ExportFormat.objects.get(slug='garmin')
        celery_uid = str(uuid.uuid4())
        # shp export task mock
        shp_export_task = mock_shp.return_value
        shp_export_task.run.return_value = Mock(state='PENDING', id=celery_uid)
        type(shp_export_task).name = PropertyMock(return_value='Shapefile Export')
        garmin_export_task = mock_garmin.return_value
        garmin_export_task.run.return_value = Mock(state='PENDING', id=celery_uid)
        type(garmin_export_task).name = PropertyMock(return_value='Garmin Export')
        type(garmin_export_task).region = PropertyMock(return_value='Africa')
        # celery chain mock
        celery_chain = mock_chain.return_value
        celery_chain.apply_async.return_value = Mock()
        self.job.formats = [shp_task, garmin_task]
        runner = ExportTaskRunner()
        runner.run_task(job_uid=self.uid)
        run = self.job.runs.all()[0]
        self.assertIsNotNone(run)
        # assert delay method called on mock chord..
        celery_chain.delay.assert_called_once()
        tasks = run.tasks.all()
        self.assertIsNotNone(tasks)
        self.assertEquals(6, len(tasks))  # 4 initial tasks + 1 shape export task
        self.assertFalse(hasattr(tasks[0], 'result'))  # no result yet..
