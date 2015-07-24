import logging
import json
import sys
import os
from django.test import TestCase
from django.utils import timezone
from django.core.files import File
from unittest import skip
from ..presets import PresetParser, DEFAULT_TAGS
from ..hdm_tags import HOT_HDM

logger = logging.getLogger(__name__)

class TestPresetParser(TestCase):
    
    def setUp(self,):
        self.path = os.path.dirname(os.path.realpath(__file__))
    
    def test_parse_preset(self,):
        parser = PresetParser(self.path + '/files/hdm_presets.xml')
        tags = parser.parse()
        self.assertIsNotNone(tags)
        self.assertEquals(30, len(tags))
        
        #  logger.debug('\n\t======== USER TAGS ==========\n')
        #logger.debug('User tags: %s' % tags.keys())
        categories = parser.categorise_tags(tags)
        #logger.debug('Points: %s\n' % sorted(categories['points']))
        #logger.debug('Lines: %s\n' % sorted(categories['lines']))
        #logger.debug('Polygons: %s\n' % sorted(categories['polygons']))
        
    def test_merge_presets(self, ):
        parser = PresetParser(self.path + '/files/hdm_presets.xml')
        tags = parser.parse()
        merged = parser.merge_presets(tags)
        
        #logger.debug('\n\t======== DEFAULT TAGS ==========\n')
        categories = parser.categorise_tags(DEFAULT_TAGS)
        #logger.debug('Points: %s\n' % sorted(categories['points']))
        #logger.debug('Lines: %s\n' % sorted(categories['lines']))
        #logger.debug('Polygons: %s\n' % sorted(categories['polygons']))
        
        #logger.debug('\n\t======== MERGED TAGS ==========\n')
        categories = parser.categorise_tags(merged)
        #logger.debug('Points: %s\n' % sorted(categories['points']))
        #logger.debug('Lines: %s\n' % sorted(categories['lines']))
        #logger.debug('Polygons: %s\n' % sorted(categories['polygons']))
        
        # check merged points
        self.assertTrue('borehole' in categories['points'])
        self.assertTrue('emergency' in categories['points'])
        self.assertTrue('tank' in categories['points'])
        
        #check lines
        self.assertTrue('aeroway'in categories['lines'])
        self.assertTrue('ford'in categories['lines'])
        self.assertTrue('man_made' in categories['lines'])
        
        # check polygons
        self.assertTrue('area' in categories['polygons'])
        self.assertTrue('information' in categories['polygons'])
        self.assertTrue('junction' in categories['polygons'])
        self.assertTrue('office' in categories['polygons'])
        self.assertTrue('tank' in categories['polygons'])


class TestHDMToJSON(TestCase):
    
    def setUp(self, ):
        self.path = os.path.dirname(os.path.realpath(__file__))
    
    def test_hdm_to_json(self,):
        js = json.dumps(HOT_HDM, sort_keys=False)
        f = open(self.path + '/hdm.json', 'w')
        f.write(js)
        f.close()
        