import sys
import os

from django.test import TestCase
from django.utils import timezone
from unittest import skip
from jobs import presets

from ..osmconf import OSMConfig


class TestOSMConf(TestCase):
    
    def setUp(self,):
        self.path = os.path.dirname(os.path.realpath(__file__))
        #self.conf = self.path = '/'
        parser = presets.PresetParser(self.path + '/files/hot_field_collection_presets.xml')
        self.tags = parser.parse(merge_with_defaults=True)
        self.assertIsNotNone(self.tags)
        self.assertEquals(70, len(self.tags))
        self.categories = parser.categorise_tags(self.tags)
    
    def test_create_osm_conf(self,):
        conf = OSMConfig(self.categories)
        conf.create_osm_conf()