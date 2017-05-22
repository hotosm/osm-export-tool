# -*- coding: utf-8 -*-
import logging
import os

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry, Polygon
from django.core.files import File
from django.test import TestCase
from django.utils import timezone

import jobs.presets as presets
from jobs.models import (
    ExportConfig, ExportProfile, Job, Tag
)

LOG = logging.getLogger(__name__)


class TestJob(TestCase):
    """
    Test cases for Job model
    """

    def setUp(self,):
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.formats = settings.EXPORT_FORMATS.keys()
        Group.objects.create(name='TestDefaultExportExtentGroup')
        self.user = User.objects.create(
            username='demo', email='demo@demo.com', password='demo')
        bbox = Polygon.from_bbox((-7.96, 22.6, -8.14, 27.12))
        the_geom = GEOSGeometry(bbox, srid=4326)
        self.job = Job(name='TestJob',
                       description='Test description', event='Nepal activation',
                       user=self.user, the_geom=the_geom)
        self.job.save()
        self.uid = self.job.uid
        # add the formats to the job
        self.job.export_formats = self.formats
        self.job.save()
        self.tags = [('building', 'yes'), ('place', 'city'),
                     ('highway', 'service'), ('aeroway', 'helipad')]
        for tag in self.tags:
            tag = Tag.objects.create(
                key=tag[0],
                value=tag[1],
                job=self.job
            )

    def test_job_creation(self,):
        saved_job = Job.objects.all()[0]
        self.assertEqual(self.job, saved_job)
        self.assertEquals(self.uid, saved_job.uid)
        self.assertIsNotNone(saved_job.created_at)
        self.assertIsNotNone(saved_job.updated_at)
        saved_formats = saved_job.export_formats
        self.assertIsNotNone(saved_formats)
        self.assertItemsEqual(saved_formats, self.formats)
        tags = saved_job.tags.all()
        self.assertEquals(4, len(tags))
        self.assertEquals('Test description', saved_job.description)
        self.assertIsNone(saved_job.config)

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

    def test_spatial_fields(self,):
        bbox = Polygon.from_bbox((-7.96, 22.6, -8.14, 27.12))  # in africa
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
        self.assertEquals('Nepal activation', job.event)
        self.assertEqual(self.user, job.user)

    def test_str(self, ):
        job = Job.objects.all()[0]
        self.assertEquals(str(job), 'TestJob')

    def test_overpass_extents(self,):
        job = Job.objects.all()[0]
        extents = job.overpass_extents
        self.assertIsNotNone(extents)
        self.assertEquals(4, len(extents.split(',')))

