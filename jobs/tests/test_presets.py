import logging
import sys
import os
from django.test import TestCase
from django.utils import timezone
from django.core.files import File
from ..presets import PresetParser, DEFAULT_TAGS

logger = logging.getLogger(__name__)

class TestPresetParser(TestCase):
    
    def setUp(self,):
        self.path = os.path.dirname(os.path.realpath(__file__))
    
    def test_parse_preset(self,):
        parser = PresetParser(self.path + '/files/hot_field_collection_presets.xml')
        tags = parser.parse()
        self.assertIsNotNone(tags)
        self.assertEquals(30, len(tags))
        #logger.debug('User tags: %s' % tags.keys())
        
    def test_merge_presets(self, ):
        parser = PresetParser(self.path + '/files/hot_field_collection_presets.xml')
        tags = parser.parse()
        merged = parser.merge_presets(tags)
        #logger.debug('Default tags %s' % DEFAULT_TAGS.keys())
        #logger.debug('\nMerged tags: %s' % merged)
    
    def test_cagegorise_tags(self, ):
        parser = PresetParser(self.path + '/files/hot_field_collection_presets.xml')
        tags = parser.parse()
        categories = parser.categorise_tags(tags)
        #logger.debug('Points: %s' % categories['points'])
        #logger.debug('Lines: %s' % categories['lines'])
        #logger.debug('Polygons: %s' % categories['polygons'])
        