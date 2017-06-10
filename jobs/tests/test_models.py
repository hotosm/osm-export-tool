# -*- coding: utf-8 -*-
import logging
from unittest import skip

from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry, Polygon
from django.core.exceptions import ValidationError
from django.test import TestCase

from jobs.models import Job

LOG = logging.getLogger(__name__)

class TestJob(TestCase):
    def setUp(self,):
        user = User.objects.create(
            username='demo', email='demo@demo.com', password='demo')
        the_geom = Polygon.from_bbox((-10.80029,6.3254236,-10.79809,6.32752))
        self.fixture = {
            'name': 'TestJob',
            'description': 'Test Description',
            'event': 'Nepal Activation',
            'user': user,
            'the_geom': the_geom,
            'export_formats': ['shp']
        }

    def test_job_creation(self):
        job = Job(**self.fixture)
        job.full_clean()
        job.save()
        self.assertIsNotNone(job.uid)
        self.assertIsNotNone(job.created_at)
        self.assertIsNotNone(job.updated_at)

    def test_missing_aoi(self):
        del self.fixture['the_geom']
        job = Job(**self.fixture)
        with self.assertRaises(ValidationError) as e:
            job.full_clean()
        self.assertTrue('the_geom' in e.exception.message_dict)

    def test_export_formats(self):
        self.fixture['export_formats'] = []
        job = Job(**self.fixture)
        with self.assertRaises(ValidationError) as e:
            job.full_clean()
        self.assertTrue('export_formats' in e.exception.message_dict)

        self.fixture['export_formats'] = ['not_a_format']
        job = Job(**self.fixture)
        with self.assertRaises(ValidationError) as e:
            job.full_clean()
        self.assertTrue('export_formats' in e.exception.message_dict)

    def test_max_lengths(self):
        self.fixture['name'] = 'a' * 101
        job = Job(**self.fixture)
        with self.assertRaises(ValidationError) as e:
            job.full_clean()
        self.assertTrue('name' in e.exception.message_dict)

    def test_max_aoi_extent(self):
        self.fixture['the_geom'] = Polygon.from_bbox((0,0,1,1))
        job = Job(**self.fixture)
        with self.assertRaises(ValidationError) as e:
            job.full_clean()
        self.assertTrue('the_geom' in e.exception.message_dict)
        

    @skip('')
    def test_job_creation_with_config(self,):
        saved_job = Job.objects.all()[0]
        self.assertEqual(self.job, saved_job)
        self.assertEquals(self.uid, saved_job.uid)
        self.assertIsNotNone(saved_job.created_at)
        self.assertIsNotNone(saved_job.updated_at)
        saved_formats = saved_job.export_formats
        self.assertIsNotNone(saved_formats)
        self.assertItemsEqual(saved_formats, self.formats)
        # attach a configuration to a job
        f = File(open(self.path + '/files/hdm_presets.xml'))
        filename = f.name.split('/')[-1]
        config = ExportConfig.objects.create(name='Test Preset Config', filename=filename,
                                             upload=f, config_type='PRESET', user=self.user)
        f.close()
        self.assertIsNotNone(config)
        saved_job.config = config
        saved_job.save()
        saved_config = saved_job.config
        self.assertEqual(config, saved_config)
        saved_config.delete()  # cleanup



    @skip('')
    def test_overpass_extents(self,):
        job = Job.objects.all()[0]
        extents = job.overpass_extents
        self.assertIsNotNone(extents)
        self.assertEquals(4, len(extents.split(',')))

