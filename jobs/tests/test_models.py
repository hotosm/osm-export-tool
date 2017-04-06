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

    def test_categorised_tags(self, ):
        # delete existing tags
        self.job.tags.all().delete()
        parser = presets.PresetParser(self.path + '/files/hdm_presets.xml')
        tags = parser.parse()
        self.assertIsNotNone(tags)
        self.assertEquals(238, len(tags))
        # save all the tags from the preset
        for tag_dict in tags:
            Tag.objects.create(
                key=tag_dict['key'],
                value=tag_dict['value'],
                job=self.job,
                data_model='osm',
                geom_types=tag_dict['geom_types']
            )
        self.assertEquals(238, self.job.tags.all().count())

        job = Job.objects.all()[0]
        categories = job.categorised_tags
        self.assertIsNotNone(categories)
        self.assertEquals(24, len(categories['points']))
        self.assertEquals(12, len(categories['lines']))
        self.assertEquals(22, len(categories['polygons']))

    def test_tags(self,):
        self.job.tags.all().delete()
        parser = presets.PresetParser(self.path + '/files/hdm_presets.xml')
        tags = parser.parse()
        self.assertIsNotNone(tags)
        self.assertEquals(238, len(tags))
        # save all the tags from the preset
        for tag_dict in tags:
            Tag.objects.create(
                key=tag_dict['key'],
                value=tag_dict['value'],
                job=self.job,
                data_model='osm',
                geom_types=tag_dict['geom_types']
            )
        self.assertEquals(238, self.job.tags.all().count())


class TestExportConfig(TestCase):

    def setUp(self,):
        self.path = os.path.dirname(os.path.realpath(__file__))
        Group.objects.create(name='TestDefaultExportExtentGroup')
        self.user = User.objects.create(
            username='demo', email='demo@demo.com', password='demo')
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
        config = ExportConfig.objects.create(
            name=name, filename=filename, upload=test_file, config_type='PRESET', user=self.user)
        test_file.close()
        self.assertIsNotNone(config)
        uid = config.uid
        saved_config = ExportConfig.objects.get(uid=uid)
        self.assertEquals('PRESET', saved_config.config_type)
        self.assertEquals(name, saved_config.name)
        self.assertFalse(saved_config.published)
        self.assertIsNotNone(saved_config)
        self.assertEqual(config, saved_config)
        sf = File(open(os.path.abspath('.') +
                       '/media/export/config/preset/hdm_presets.xml'))
        self.assertIsNotNone(sf)  # check the file gets created on disk
        saved_config.delete()  # clean up
        sf.close()

    def test_add_config_to_job(self,):
        f = open(self.path + '/files/hdm_presets.xml')
        test_file = File(f)
        filename = test_file.name.split('/')[-1]
        name = 'Test Configuration File'
        config = ExportConfig.objects.create(
            name=name, filename=filename, upload=test_file, config_type='PRESET', user=self.user)
        test_file.close()
        self.assertIsNotNone(config)
        self.job.config = config
        self.assertIsNotNone(self.job.config)


class TestTag(TestCase):

    def setUp(self, ):
        self.formats = settings.EXPORT_FORMATS.keys()
        Group.objects.create(name='TestDefaultExportExtentGroup')
        self.user = User.objects.create(
            username='demo', email='demo@demo.com', password='demo')
        bbox = Polygon.from_bbox((-7.96, 22.6, -8.14, 27.12))
        the_geom = GEOSGeometry(bbox, srid=4326)
        self.job = Job.objects.create(name='TestJob',
                                      description='Test description', user=self.user,
                                      the_geom=the_geom)
        self.uid = self.job.uid
        self.job.export_formats = self.formats
        self.job.save()
        self.path = os.path.dirname(os.path.realpath(__file__))

    def test_create_tags(self,):
        tags = [
            {
                'name': 'Airport Ground',
                'key': 'aeroway',
                'value': 'aerodrome',
                'geom_types': ['node', 'area'],
                'groups': [
                    'HOT Presets v2.11',
                    'Transportation',
                    'Transportation means',
                    'Airport',
                ],
            },
        ]
        for tag_dict in tags:
            Tag.objects.create(
                key=tag_dict['key'],
                value=tag_dict['value'],
                job=self.job,
                data_model='osm',
                geom_types=tag_dict['geom_types'],
                groups=tag_dict['groups']
            )
        saved_tags = Tag.objects.all()
        self.assertEquals(saved_tags[0].key, 'aeroway')
        geom_types = saved_tags[0].geom_types
        self.assertEquals(1, len(saved_tags))
        self.assertEqual(['node', 'area'], geom_types)
        groups = saved_tags[0].groups
        self.assertEquals(4, len(groups))

    def test_save_tags_from_preset(self,):
        parser = presets.PresetParser(self.path + '/files/hdm_presets.xml')
        tags = parser.parse()
        self.assertIsNotNone(tags)
        self.assertEquals(238, len(tags))
        for tag_dict in tags:
            Tag.objects.create(
                key=tag_dict['key'],
                value=tag_dict['value'],
                job=self.job,
                data_model='osm',
                geom_types=tag_dict['geom_types'],
                groups=tag_dict['groups']
            )
        self.assertEquals(238, self.job.tags.all().count())
        # check the groups got saved correctly
        saved_tag = self.job.tags.filter(value='service')[0]
        self.assertIsNotNone(saved_tag)
        self.assertEquals(3, len(saved_tag.groups))

    def test_get_categorised_tags(self,):
        parser = presets.PresetParser(self.path + '/files/hdm_presets.xml')
        tags = parser.parse()
        self.assertIsNotNone(tags)
        self.assertEquals(238, len(tags))
        for tag_dict in tags:
            Tag.objects.create(
                key=tag_dict['key'],
                value=tag_dict['value'],
                job=self.job,
                data_model='osm',
                geom_types=tag_dict['geom_types'],
                groups=tag_dict['groups']
            )
        self.assertEquals(238, self.job.tags.all().count())
