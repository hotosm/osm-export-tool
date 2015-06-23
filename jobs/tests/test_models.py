import logging
import sys
import uuid
import os
from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry, Polygon
from jobs.models import Job, ExportFormat, Region, ExportConfig, Tag
from tasks.models import ExportTask, ExportRun
from django.contrib.gis.gdal import DataSource
from django.utils import timezone
from django.core.files import File

import jobs.presets as presets

logger = logging.getLogger(__name__)   


class TestJob(TestCase):
    """
    Test cases for Job model
    """
    def setUp(self,):
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.formats = ExportFormat.objects.all() #pre-loaded by 'insert_export_formats' migration
        self.user = User.objects.create(username='demo', email='demo@demo.com', password='demo')
        bbox = Polygon.from_bbox((-7.96, 22.6, -8.14, 27.12))
        the_geom = GEOSGeometry(bbox, srid=4326)
        self.job = Job.objects.create(name='TestJob',
                                 description='Test description', user=self.user,
                                 the_geom=the_geom)
        self.uid = self.job.uid
        # add the formats to the job
        self.job.formats = self.formats
        self.job.save()
        preset_parser = presets.PresetParser(preset=self.path + '/files/hdm_presets.xml')
        tags = preset_parser.parse(merge_with_defaults=False)
        for key in tags:
            tag = Tag.objects.create(
                name = key,
                geom_types = tags[key]
            )
            self.job.tags.add(tag)
        
    
    def test_job_creation(self,):
        saved_job = Job.objects.all()[0]
        self.assertEqual(self.job, saved_job)
        self.assertEquals(self.uid, saved_job.uid)
        self.assertIsNotNone(saved_job.created_at)
        self.assertIsNotNone(saved_job.updated_at)
        saved_formats = saved_job.formats.all()
        self.assertIsNotNone(saved_formats)
        self.assertItemsEqual(saved_formats, self.formats)
        
    def test_job_creation_with_config(self,):
        saved_job = Job.objects.all()[0]
        self.assertEqual(self.job, saved_job)
        self.assertEquals(self.uid, saved_job.uid)
        self.assertIsNotNone(saved_job.created_at)
        self.assertIsNotNone(saved_job.updated_at)
        saved_formats = saved_job.formats.all()
        self.assertIsNotNone(saved_formats)
        self.assertItemsEqual(saved_formats, self.formats)
        # attach a configuration to a job
        f = File(open(self.path + '/files/hdm_presets.xml'))
        filename = f.name.split('/')[-1]
        config = ExportConfig.objects.create(name='Test Preset Config', filename=filename,
                                             upload=f, config_type='PRESET', user=self.user)
        f.close()
        self.assertIsNotNone(config)
        uid = config.uid
        saved_job.configs.add(config)
        saved_config = saved_job.configs.all()[0]
        self.assertEqual(config, saved_config)
        saved_config.delete() #cleanup
        
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
        
    def test_overpass_extents(self,):
        job = Job.objects.all()[0]
        extents = job.overpass_extents
        self.assertIsNotNone(extents)
        self.assertEquals(4, len(extents.split(',')))
        
    def test_categorised_tags(self, ):
        job = Job.objects.all()[0]
        categories = job.categorised_tags
        self.assertIsNotNone(categories)
        self.assertEqual(24, len(categories['points']))
    

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
        self.job = Job.objects.create(name='TestJob',
                                 description='Test description', user=self.user,
                                 the_geom=the_geom)
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
        job.the_geom = the_geom
        job.save()
        regions = Region.objects.filter(the_geom__intersects=job.the_geom).intersection(job.the_geom, field_name='the_geom').order_by( '-intersection')
        self.assertEquals(0, len(regions))


class TestExportConfig(TestCase):
    
    def setUp(self,):
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.user = User.objects.create(username='demo', email='demo@demo.com', password='demo')
        bbox = Polygon.from_bbox((-7.96, 22.6, -8.14, 27.12))
        the_geom = GEOSGeometry(bbox, srid=4326)
        self.job = Job.objects.create(name='TestJob',
                                 description='Test description', user=self.user,
                                 the_geom=the_geom)
        self.uid = self.job.uid
        
    
    def test_create_config(self,):
        f = open(self.path + '/files/hdm_presets.xml')
        test_file = File(f)
        filename = test_file.name.split('/')[-1]
        name = 'Test Configuration File'
        config = ExportConfig.objects.create(name=name, filename=filename, upload=test_file, config_type='PRESET', user=self.user)
        test_file.close()
        self.assertIsNotNone(config)
        uid = config.uid
        saved_config = ExportConfig.objects.get(uid=uid)
        self.assertEquals('PRESET', saved_config.config_type)
        self.assertEquals(name, saved_config.name)
        self.assertTrue(saved_config.visible)
        self.assertIsNotNone(saved_config)
        self.assertEqual(config, saved_config)
        sf = File(open(os.path.abspath('.') + '/media/export/config/preset/hdm_presets.xml'))
        self.assertIsNotNone(sf) # check the file gets created on disk
        saved_config.delete() # clean up
        sf.close()
        
class TestTag(TestCase):
    
    def setUp(self, ):
        self.formats = ExportFormat.objects.all() #pre-loaded by 'insert_export_formats' migration
        self.user = User.objects.create(username='demo', email='demo@demo.com', password='demo')
        bbox = Polygon.from_bbox((-7.96, 22.6, -8.14, 27.12))
        the_geom = GEOSGeometry(bbox, srid=4326)
        self.job = Job.objects.create(name='TestJob',
                                 description='Test description', user=self.user,
                                 the_geom=the_geom)
        self.uid = self.job.uid
        # add the formats to the job
        self.job.formats = self.formats
        self.job.save()
        self.path = os.path.dirname(os.path.realpath(__file__))
        
    def test_create_tags(self,):
        self.default_tags = presets.DEFAULT_TAGS
        parser = presets.PresetParser(self.path + '/files/hdm_presets.xml')
        self.user_tags = parser.parse()
        for key in self.user_tags:
            tag = Tag.objects.create(
                name = key,
                geom_types = self.user_tags[key]
            )
            self.job.tags.add(tag)
        tags = Tag.objects.all()
        self.assertEquals(30, len(tags))
        
    
        
    
    
        