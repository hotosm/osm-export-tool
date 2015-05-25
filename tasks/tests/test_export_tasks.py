# test cases for HOT Export Tasks
import logging
import json
import uuid
from django.test import TestCase
from django.contrib.auth.models import User
from mock import Mock, patch, PropertyMock
from ..export_tasks import ExportTaskRunner, ShpExportTask
from jobs.models import ExportFormat, Job
from django.contrib.gis.geos import GEOSGeometry

logger = logging.getLogger(__name__)

class TestExportTaskRunner(TestCase):
    
    def setUp(self,):
        self.formats = [ExportFormat.objects.get(slug='shp')] #pre-loaded by 'insert_export_formats' migration
        self.user = User.objects.create(username='demo', email='demo@demo.com', password='demo')
        bbox_wkt = 'POLYGON((10 10, 10 20, 20 20, 20 10, 10 10))'
        the_geom = GEOSGeometry(bbox_wkt, srid=4326)
        the_geog = GEOSGeometry(bbox_wkt)
        the_geom_webmercator = the_geom.transform(ct=3857, clone=True)
        self.job = Job.objects.create(name='TestJob',
                                 description='Test description', user=self.user,
                                 the_geom=the_geom, the_geog=the_geog,
                                 the_geom_webmercator=the_geom_webmercator)
        self.uid = str(self.job.uid)
        # add the formats to the job
        self.job.formats = self.formats
        self.job.save()
    
    @patch('tasks.export_tasks.ShpExportTask')
    def test_run_shp_export_task(self, mock):
        shp_export_task = mock.return_value
        shp_export_task.delay.return_value = Mock(state='PENDING')
        runner = ExportTaskRunner()
        runner.run_task(job_uid=self.uid)
        shp_export_task.delay.assert_called_with(job_uid=self.uid)
        shp_export_task.delay.return_value.assert_called('state')
