import logging
import sys
import uuid
import os
from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry
from jobs.models import ExportTask, Job, ExportFormat, Region
from django.contrib.gis.gdal import DataSource

logger = logging.getLogger(__name__)   
    

class TestExportTask(TestCase):
    """
    Test cases for ExportTask model
    """
    def setUp(self,):
        formats = ExportFormat.objects.all()
        user = User.objects.create(username='demo', email='demo@demo.com', password='demo')
        bbox_wkt = 'POLYGON((10 10, 10 20, 20 20, 20 10, 10 10))'
        the_geom = GEOSGeometry(bbox_wkt, srid=4326)
        the_geog = GEOSGeometry(bbox_wkt)
        the_geom_webmercator = the_geom.transform(ct=3857, clone=True)
        Job.objects.create(name='TestJob',
                                 description='Test description', user=user,
                                 the_geom=the_geom, the_geog=the_geog,
                                 the_geom_webmercator=the_geom_webmercator)
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
        bbox_wkt = 'POLYGON((10 10, 10 20, 20 20, 20 10, 10 10))'
        the_geom = GEOSGeometry(bbox_wkt, srid=4326)
        the_geog = GEOSGeometry(bbox_wkt)
        the_geom_webmercator = the_geom.transform(ct=3857, clone=True)
        self.job = Job.objects.create(name='TestJob',
                                 description='Test description', user=self.user,
                                 the_geom=the_geom, the_geog=the_geog,
                                 the_geom_webmercator=the_geom_webmercator)
        self.uid = self.job.uid
        # add the formats to the job
        self.job.formats = self.formats
        self.job.save()
        
    
    def test_job_creation(self,):
        saved_job = Job.objects.all()[0]
        self.assertEqual(self.job, saved_job)
        self.assertEquals(self.uid, saved_job.uid)
        self.assertIsNotNone(saved_job.created_at)
        self.assertIsNotNone(saved_job.updated_at)
        self.assertEquals('', saved_job.status)
        saved_formats = saved_job.formats.all()
        self.assertIsNotNone(saved_formats)
        self.assertItemsEqual(saved_formats, self.formats)
    
    
    def test_spatial_fields(self,):
        bbox_wkt = 'POLYGON((10 10, 10 20, 20 20, 20 10, 10 10))'
        the_geom = GEOSGeometry(bbox_wkt, srid=4326)
        the_geog = GEOSGeometry(bbox_wkt)
        the_geom_webmercator = the_geom.transform(ct=3857, clone=True)
        job = Job.objects.all()[0]
        self.assertIsNotNone(job)
        geom = job.the_geom
        geog = job.the_geog
        geom_web = job.the_geom_webmercator
        self.assertEqual(the_geom, geom)
        self.assertEqual(the_geog, geog)
        self.assertEqual(the_geom_webmercator, geom_web)
        
    def test_fields(self, ):
        job = Job.objects.all()[0]
        self.assertEquals('TestJob', job.name)
        self.assertEquals('Test description', job.description)
        self.assertEqual(self.user, job.user)
        
    def test_str(self, ):
        job = Job.objects.all()[0]
        self.assertEquals(str(job), 'TestJob')
    


class TestExportFormat(TestCase):
    
    def test_str(self,):
        kml = ExportFormat.objects.get(slug='kml')
        self.assertEquals(unicode(kml), 'kml')
        self.assertEquals(str(kml), 'KML Format')
        

class TestRegion(TestCase):
    
    def setUp(self,):
        self.ds = DataSource(os.path.dirname(os.path.realpath(__file__)) + '../migrations/africa.geojson')
        
    def test_load_region(self,):
        layer = self.ds[0]
        geom = layer.get_geoms(geos=True)[0]
        the_geom = GEOSGeometry(geom.wkt, srid=4326)
        the_geog = GEOSGeometry(geom.wkt)
        the_geom_webmercator = the_geom.transform(ct=3857, clone=True)
        region = Region.objects.create(name="Africa", description="African export region",
                        the_geom=the_geom, the_geog=the_geog, the_geom_webmercator=the_geom_webmercator
        )
        logger.debug(region.uid)
        saved_region = Region.objects.get(uid=region.uid)
        self.assertEqual(region, saved_region)

