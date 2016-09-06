# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging
import os
from StringIO import StringIO
from unittest import skip

from lxml import etree

from django.contrib.auth.models import Group, User
from django.contrib.gis.geos import GEOSGeometry, Polygon
from django.core.files import File
from django.core.files.base import ContentFile
from django.test import TestCase

from ..models import ExportConfig, ExportFormat, Job, Tag
from ..presets import PresetParser, TagParser, UnfilteredPresetParser

logger = logging.getLogger(__name__)


class TestPresetParser(TestCase):

    def setUp(self,):
        self.path = os.path.dirname(os.path.realpath(__file__))

    def test_parse_preset(self,):
        parser = PresetParser(self.path + '/files/hdm_presets.xml')
        tags = parser.parse()
        self.assertIsNotNone(tags)
        self.assertEquals(238, len(tags))

    def test_validate_hdm_presets(self, ):
        schema = StringIO(open(self.path + '/files/tagging-preset.xsd').read())
        xmlschema_doc = etree.parse(schema)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        xml = StringIO(open(self.path + '/files/hdm_presets.xml').read())
        tree = etree.parse(xml)
        valid = xmlschema.validate(tree)
        self.assertTrue(valid)

    def test_validate_osm_presets(self, ):
        schema = StringIO(open(self.path + '/files/tagging-preset.xsd').read())
        xmlschema_doc = etree.parse(schema)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        xml = StringIO(open(self.path + '/files/osm_presets.xml').read())
        tree = etree.parse(xml)
        valid = xmlschema.validate(tree)
        self.assertTrue(valid)

    def test_validate_custom_preset(self, ):
        schema = StringIO(open(self.path + '/files/tagging-preset.xsd').read())
        xmlschema_doc = etree.parse(schema)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        xml = StringIO(open(self.path + '/files/custom_preset.xml').read())
        tree = etree.parse(xml)
        valid = xmlschema.validate(tree)
        self.assertTrue(valid)

    def test_build_hdm_preset_dict(self,):
        parser = PresetParser(self.path + '/files/hdm_presets.xml')
        group_dict = parser.build_hdm_preset_dict()
        # logger.debug(group_dict)
        # logger.debug(json.dumps(group_dict, indent=4, sort_keys=True))

    def test_build_osm_preset_dict(self,):
        parser = PresetParser(self.path + '/files/osm_presets.xml')
        group_dict = parser.build_hdm_preset_dict()
        # logger.debug(group_dict)
        # logger.debug(json.dumps(group_dict, indent=4, sort_keys=True))


class TestUnfilteredPresetParser(TestCase):

    def setUp(self,):
        self.path = os.path.dirname(os.path.realpath(__file__))
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

    def test_parse_preset(self,):
        parser = UnfilteredPresetParser(self.path + '/files/hdm_presets.xml')
        tags = parser.parse()
        self.assertIsNotNone(tags)
        self.assertEquals(233, len(tags))

    def test_validate_hdm_presets(self, ):
        schema = StringIO(open(self.path + '/files/tagging-preset.xsd').read())
        xmlschema_doc = etree.parse(schema)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        xml = StringIO(open(self.path + '/files/hdm_presets.xml').read())
        tree = etree.parse(xml)
        valid = xmlschema.validate(tree)
        self.assertTrue(valid)

    def test_validate_osm_presets(self, ):
        schema = StringIO(open(self.path + '/files/tagging-preset.xsd').read())
        xmlschema_doc = etree.parse(schema)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        xml = StringIO(open(self.path + '/files/osm_presets.xml').read())
        tree = etree.parse(xml)
        valid = xmlschema.validate(tree)
        self.assertTrue(valid)

    def test_build_hdm_preset_dict(self,):
        parser = UnfilteredPresetParser(self.path + '/files/hdm_presets.xml')
        group_dict = parser.build_hdm_preset_dict()
        # logger.debug(group_dict)
        # logger.debug(json.dumps(group_dict, indent=4, sort_keys=True))

    def test_build_osm_preset_dict(self,):
        parser = UnfilteredPresetParser(self.path + '/files/osm_presets.xml')
        group_dict = parser.build_hdm_preset_dict()
        # logger.debug(group_dict)
        # logger.debug(json.dumps(group_dict, indent=4, sort_keys=True))

    def test_save_tags(self, ):
        parser = UnfilteredPresetParser(self.path + '/files/hdm_presets.xml')
        tags = parser.parse()
        self.assertIsNotNone(tags)
        self.assertEquals(233, len(tags))
        for tag_dict in tags:
            tag = Tag.objects.create(
                name=tag_dict['name'],
                key=tag_dict['key'],
                value=tag_dict['value'],
                job=self.job,
                data_model='PRESET',
                geom_types=tag_dict['geom_types'],
                groups=tag_dict['groups']
            )
        self.assertEquals(233, self.job.tags.all().count())


class TestTagParser(TestCase):
    """Test generation of preset from HDM tags."""

    def setUp(self, ):
        self.path = os.path.dirname(os.path.realpath(__file__))
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

        # add tags
        parser = PresetParser(self.path + '/files/hdm_presets.xml')
        tags = parser.parse()
        self.assertIsNotNone(tags)
        self.assertEquals(238, len(tags))
        for tag_dict in tags:
            tag = Tag.objects.create(
                name=tag_dict['name'],
                key=tag_dict['key'],
                value=tag_dict['value'],
                job=self.job,
                data_model='PRESET',
                geom_types=tag_dict['geom_types'],
                groups=tag_dict['groups']
            )
        self.assertEquals(238, self.job.tags.all().count())

    def test_parse_tags(self,):
        job = Job.objects.all()[0]
        tag_parser = TagParser(tags=job.tags.all())
        xml = tag_parser.parse_tags()
        test_file = ContentFile(xml)
        name = 'Custom HDM Preset'
        filename = 'hdm_custom_preset.xml'
        content_type = 'application/xml'
        config = ExportConfig.objects.create(
            name=name, filename=filename,
            config_type='PRESET', content_type=content_type,
            user=self.user
        )
        config.upload.save(filename, test_file)
        self.assertIsNotNone(config)
        uid = config.uid
        saved_config = ExportConfig.objects.get(uid=uid)
        self.assertEquals('PRESET', saved_config.config_type)
        self.assertEquals(name, saved_config.name)
        self.assertFalse(saved_config.published)
        self.assertIsNotNone(saved_config)
        self.assertEqual(config, saved_config)
        self.assertIsNotNone(saved_config.upload)
        # logger.debug(saved_config.upload)
        sf = File(open(os.path.abspath('.') + '/media/export/config/preset/hdm_custom_preset.xml'))
        self.assertIsNotNone(sf)  # check the file gets created on disk
        sf.close()

        # validate the custom preset
        schema = StringIO(open(self.path + '/files/tagging-preset.xsd').read())
        xmlschema_doc = etree.parse(schema)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        xml = StringIO(open(os.path.abspath('.') + saved_config.upload.url).read())
        tree = etree.parse(xml)
        valid = xmlschema.validate(tree)
        self.assertTrue(valid)
        saved_config.delete()  # clean up
