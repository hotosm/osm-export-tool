# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.contrib.gis.geos import GEOSGeometry, Polygon
from django.test import TestCase

from oet2.jobs import presets
from oet2.jobs.models import ExportFormat, Job, Tag

from ..osmconf import OSMConfig


class TestOSMConf(TestCase):

    def setUp(self,):
        self.path = settings.ABS_PATH()
        parser = presets.PresetParser(self.path + '/utils/tests/files/hdm_presets.xml')
        self.tags = parser.parse()
        self.assertIsNotNone(self.tags)
        self.assertEquals(256, len(self.tags))
        self.formats = ExportFormat.objects.all()  # pre-loaded by 'insert_export_formats' migration
        Group.objects.create(name='TestDefaultExportExtentGroup')
        self.user = User.objects.create(username='demo', email='demo@demo.com', password='demo')
        bbox = Polygon.from_bbox((-7.96, 22.6, -8.14, 27.12))
        the_geom = GEOSGeometry(bbox, srid=4326)
        self.job = Job.objects.create(name='TestJob',
                                 description='Test description', event='Nepal activation',
                                 user=self.user, the_geom=the_geom)
        self.uid = self.job.uid
        # add the formats to the job
        self.job.formats = self.formats
        self.job.save()
        for tag in self.tags:
            Tag.objects.create(
                key=tag['key'],
                value=tag['value'],
                job=self.job,
                data_model='osm',
                geom_types=tag['geom_types']
            )
        self.categories = self.job.categorised_tags

    def test_create_osm_conf(self,):
        conf = OSMConfig(self.categories, job_name=self.job.name)
        path = conf.create_osm_conf(stage_dir=self.path + '/utils/tests/files/')
        self.assertTrue(os.path.exists(path))
        os.remove(path)
