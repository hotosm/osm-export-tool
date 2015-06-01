import logging
import sys
import uuid
import os
from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry, Polygon
from jobs.models import Job, ExportFormat, Region
from tasks.models import ExportTask, ExportRun
from django.contrib.gis.gdal import DataSource
from django.utils import timezone

logger = logging.getLogger(__name__)   


class TestJob(TestCase):
    """
    Test cases for Job model
    """
    def setUp(self,):
        self.formats = ExportFormat.objects.all() #pre-loaded by 'insert_export_formats' migration
        self.user = User.objects.create(username='demo', email='demo@demo.com', password='demo')
        bbox = Polygon.from_bbox((-7.96, 22.6, -8.14, 27.12))
        the_geom = GEOSGeometry(bbox, srid=4326)
        the_geog = GEOSGeometry(bbox)
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
        bbox = Polygon.from_bbox((-7.96, 22.6, -8.14, 27.12)) # in africa
        the_geom = GEOSGeometry(bbox, srid=4326)
        the_geog = GEOSGeometry(bbox)
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
        
    def test_job_region(self, ):
        bbox = Polygon.from_bbox((-7.96, 22.6, -8.14, 27.12)) # africa
        region = Region.objects.filter(the_geom__contains=bbox)[0]
        self.assertIsNotNone(region)
        self.assertEquals('Africa', region.name)
        self.job.region = region
        self.job.save()
        saved_job = Job.objects.all()[0]
        self.assertEqual(saved_job.region, region)
    

class TestExportFormat(TestCase):
    
    def test_str(self,):
        kml = ExportFormat.objects.get(slug='kml')
        self.assertEquals(unicode(kml), 'kml')
        self.assertEquals(str(kml), 'KML Format')
        

class TestRegion(TestCase):
            
    def test_load_region(self,):
        ds = DataSource(os.path.dirname(os.path.realpath(__file__)) + '/../migrations/africa.geojson')
        layer = ds[0]
        geom = layer.get_geoms(geos=True)[0]
        the_geom = GEOSGeometry(geom.wkt, srid=4326)
        the_geog = GEOSGeometry(geom.wkt)
        the_geom_webmercator = the_geom.transform(ct=3857, clone=True)
        region = Region.objects.create(name="Africa", description="African export region",
                        the_geom=the_geom, the_geog=the_geog, the_geom_webmercator=the_geom_webmercator
        )
        saved_region = Region.objects.get(uid=region.uid)
        self.assertEqual(region, saved_region)
    
    def test_africa_region(self, ):
        africa = Region.objects.get(name='Africa')
        self.assertIsNotNone(africa)
        self.assertEquals('Africa', africa.name)
        self.assertIsNotNone(africa.the_geom)
        
    def test_bbox_intersects_region(self, ):
        bbox = Polygon.from_bbox((-3.9, 16.6, 7.0, 27.6))
        self.assertIsNotNone(bbox)
        africa = Region.objects.get(name='Africa')
        self.assertIsNotNone(africa)
        self.assertTrue(africa.the_geom.intersects(bbox))
        
    def test_get_region_for_bbox(self, ):
        bbox = Polygon.from_bbox((-3.9, 16.6, 7.0, 27.6))
        regions = Region.objects.all()
        found = []
        for region in regions:
            if region.the_geom.intersects(bbox):
                found.append(region)
                break
        self.assertTrue(len(found) == 1)
        self.assertEquals('Africa', found[0].name)
    

class TestJobRegionIntersection(TestCase):
    
    def setUp(self,):
        self.formats = ExportFormat.objects.all() #pre-loaded by 'insert_export_formats' migration
        self.user = User.objects.create(username='demo', email='demo@demo.com', password='demo')
        bbox = Polygon.from_bbox((36.90, 13.54, 48.52, 20.24)) # overlaps africa / central asia
        the_geom = GEOSGeometry(bbox, srid=4326)
        the_geog = GEOSGeometry(bbox)
        the_geom_webmercator = the_geom.transform(ct=3857, clone=True)
        self.job = Job.objects.create(name='TestJob',
                                 description='Test description', user=self.user,
                                 the_geom=the_geom, the_geog=the_geog,
                                 the_geom_webmercator=the_geom_webmercator)
        self.uid = self.job.uid
        # add the formats to the job
        self.job.formats = self.formats
        self.job.save()
        
    def test_job_region_intersection(self, ):
        job = Job.objects.all()[0]
        # use the_geog
        started = timezone.now()
        regions = Region.objects.filter(the_geog__intersects=job.the_geog).intersection(job.the_geog, field_name='the_geog').order_by( '-intersection')
        finished = timezone.now()
        geog_time = finished - started
        #logger.debug('Geography lookup took: %s' % geog_time)
        self.assertEquals(2, len(regions))
        asia = regions[0]
        africa = regions[1]
        #logger.debug('Asian Geog intersection area: %s' % asia.intersection.area)
        self.assertIsNotNone(asia)
        self.assertIsNotNone(africa)
        self.assertEquals('Central Asia/Middle East', asia.name)
        self.assertEquals('Africa', africa.name)
        self.assertTrue(asia.intersection.area > africa.intersection.area)
        
        regions = None
        
        #use the_geom
        started = timezone.now()
        regions = Region.objects.filter(the_geom__intersects=job.the_geom).intersection(job.the_geom, field_name='the_geom').order_by( '-intersection')
        finished = timezone.now()
        geom_time = finished - started
        #logger.debug('Geometry lookup took: %s' % geom_time)
        self.assertEquals(2, len(regions))
        asia = regions[0]
        africa = regions[1]
        #logger.debug('Asian Geom intersection area: %s' % asia.intersection.area)
        self.assertIsNotNone(asia)
        self.assertIsNotNone(africa)
        self.assertEquals('Central Asia/Middle East', asia.name)
        self.assertEquals('Africa', africa.name)
        self.assertTrue(asia.intersection.area > africa.intersection.area)
    
    def test_job_outside_region(self, ):
        job = Job.objects.all()[0]
        bbox = Polygon.from_bbox((2.74, 47.66, 21.61, 60.24)) # outside any region
        the_geom = GEOSGeometry(bbox, srid=4326)
        the_geog = GEOSGeometry(bbox)
        the_geom_webmercator = the_geom.transform(ct=3857, clone=True)
        job.the_geom = the_geom
        job.the_geog = the_geog
        job.the_geom_webmercator = the_geom_webmercator
        job.save()
        regions = Region.objects.filter(the_geom__intersects=job.the_geom).intersection(job.the_geom, field_name='the_geom').order_by( '-intersection')
        self.assertEquals(0, len(regions))


    