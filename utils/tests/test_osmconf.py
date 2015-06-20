import sys
import os
import uuid
from django.test import TestCase
from django.utils import timezone
from unittest import skip
from jobs import presets

from ..osmconf import OSMConfig


class TestOSMConf(TestCase):
    
    def setUp(self,):
        self.path = os.path.dirname(os.path.realpath(__file__))
        parser = presets.PresetParser(self.path + '/files/hdm_presets.xml')
        self.tags = parser.parse(merge_with_defaults=True)
        self.assertIsNotNone(self.tags)
        self.assertEquals(70, len(self.tags))
        self.categories = parser.categorise_tags(self.tags)
    
    def test_create_osm_conf(self,):
        conf = OSMConfig(self.categories)
        path = conf.create_osm_conf(stage_dir=self.path + '/files/')
        self.assertTrue(os.path.exists(path))
        os.remove(path)
        