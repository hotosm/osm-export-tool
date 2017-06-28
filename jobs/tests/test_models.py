# -*- coding: utf-8 -*-
import logging
from unittest import skip

from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry, Polygon
from django.core.exceptions import ValidationError
from django.test import TestCase

from jobs.models import Job, HDXExportRegion
from feature_selection.feature_selection import FeatureSelection

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
            'export_formats': ['shp'],
            'feature_selection':FeatureSelection.example('simple')
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

    def test_missing_fields(self):
        job = Job(**self.fixture)
        job.full_clean()
        job.save()
        self.assertIsNotNone(job.uid)
        self.assertFalse(job.buffer_aoi)

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
        self.fixture['the_geom'] = Polygon.from_bbox((0,0,30,30))
        job = Job(**self.fixture)
        with self.assertRaises(ValidationError) as e:
            job.full_clean()
        self.assertTrue('the_geom' in e.exception.message_dict)

    def test_validates_feature_selection(self):
        self.fixture['feature_selection'] = ""
        job = Job(**self.fixture)
        with self.assertRaises(ValidationError) as e:
            job.full_clean()
        self.assertTrue('feature_selection' in e.exception.message_dict)
        self.fixture['feature_selection'] = """
        - a list
        - not a dict
        """
        job = Job(**self.fixture)
        with self.assertRaises(ValidationError) as e:
            job.full_clean()
        self.assertTrue('feature_selection' in e.exception.message_dict)
        self.assertEqual(e.exception.message_dict['feature_selection'],[u'YAML must be dict, not list'])
        

class TestHDXExportRegion(TestCase):
    def setUp(self,):
        user = User.objects.create(
            username='demo', email='demo@demo.com', password='demo')
        the_geom = Polygon.from_bbox((-10.80029,6.3254236,-10.79809,6.32752))
        self.job_fixture = {
            'name': 'valid_dataset_prefix',
            'description': 'Test Description',
            'event': 'Nepal Activation',
            'user': user,
            'the_geom': the_geom,
            'export_formats': ['shp'],
            'feature_selection':FeatureSelection.example('simple')
        }
        self.job = Job.objects.create(**self.job_fixture)
        self.fixture = {
            'job':self.job,
            'locations':['SEN']
        }

    def test_region_creation(self):
        region = HDXExportRegion(**self.fixture)
        region.full_clean()
        region.save()
        self.assertIsNotNone(region.id)

    def test_region_validates_job_name(self):
        self.job_fixture['name'] = 'InvalidPrefixWithCaps'
        another_job = Job(**self.job_fixture)
        region = HDXExportRegion(job=another_job)

        with self.assertRaises(ValidationError) as e:
            region.full_clean()
        self.assertTrue('dataset_prefix' in e.exception.message_dict)
