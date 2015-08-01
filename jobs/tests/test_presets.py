import logging
import json
import sys
import os
from lxml import etree
from StringIO import StringIO
from django.test import TestCase
from django.utils import timezone
from django.core.files import File
from unittest import skip
from ..presets import PresetParser
from ..hdm_tags import HOT_HDM

logger = logging.getLogger(__name__)

class TestPresetParser(TestCase):
    
    def setUp(self,):
        self.path = os.path.dirname(os.path.realpath(__file__))
    
    def test_parse_preset(self,):
        parser = PresetParser(self.path + '/files/hdm_presets.xml')
        tags = parser.parse()
        self.assertIsNotNone(tags)
        self.assertEquals(238, len(tags))
    
    @skip
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
        parser = PresetParser(self.path + '/files/hdm_presets.xml')
        group_dict = parser.build_hdm_preset_dict()
        logger.debug(group_dict)
        logger.debug(json.dumps(group_dict, indent=4, sort_keys=True))
        
    def test_build_osm_preset_dict(self,):
        parser = PresetParser(self.path + '/files/osm_presets.xml')
        group_dict = parser.build_hdm_preset_dict()
        logger.debug(group_dict)
        logger.debug(json.dumps(group_dict, indent=4, sort_keys=True))


class TestHDMToJSON(TestCase):
    
    def setUp(self, ):
        self.path = os.path.dirname(os.path.realpath(__file__))
    
    def test_hdm_to_json(self,):
        js = json.dumps(HOT_HDM, sort_keys=False)
        f = open(self.path + '/hdm.json', 'w')
        f.write(js)
        f.close()
        