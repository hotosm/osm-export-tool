import os
from django.test import TestCase
from django.utils import timezone
from unittest import skip

from ..osmparser import OSMParser

class TestOSMParser(TestCase):
    
    def setUp(self, ):
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.osm = self.path + '/test.osm'
        self.sqlite = self.path + '/test.sqlite'
    
    
    def test_osm_parsing(self, ):
        parser = OSMParser(osm=self.osm, sqlite=self.sqlite)
        
        
    