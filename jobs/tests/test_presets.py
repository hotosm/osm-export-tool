import logging
import sys
import os
from django.test import TestCase
from django.utils import timezone
from django.core.files import File
from ..presets import PresetParser

logger = logging.getLogger(__name__)

class TestPresetParser(TestCase):
    
    def setUp(self,):
        self.path = os.path.dirname(os.path.realpath(__file__))
    
    def test_parse_preset(self,):
        parser = PresetParser(self.path + '/files/hot_field_collection_presets.xml')
        tags = parser.parse()
        self.assertIsNotNone(tags)
        self.assertEquals(30, len(tags))
        logger.debug(tags)
        logger.debug(tags.keys())