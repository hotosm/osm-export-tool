import sys
import uuid
import os
from django.test import TestCase
from django.utils import timezone
from unittest import skip

from ..osmparser import OSMParser

class TestOSMParser(TestCase):
    
    def setUp(self, ):

        points = ['aeroway', 'amenity', 'barrier', 'bladder', 'borehole', 'building',
                  'craft', 'emergency', 'ford', 'highway', 'historic', 'information',
                  'leisure', 'man_made', 'natural', 'office', 'place', 'power', 'shop',
                  'tank', 'tap', 'tourism', 'traffic_calming', 'waterway']
        lines = ['aeroway', 'amenity', 'barrier', 'ford', 'highway', 'layer',
                 'leisure', 'man_made', 'natural', 'tourism', 'tunnel', 'waterway']
        polygons =  ['aeroway', 'amenity', 'area', 'barrier', 'bladder', 'borehole',
                     'building', 'highway', 'historic', 'information', 'junction',
                     'landuse', 'leisure', 'man_made', 'natural', 'office', 'power',
                     'shop', 'surface', 'tank', 'tap', 'tourism']
        self.tag_config = {'points': points, 'lines': lines, 'polygons': polygons}
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.osm = self.path + '/test.osm'
        self.sqlite = self.path + '/test.sqlite'
        
    def test_osm_parsing(self, ):
        parser = OSMParser(osm=self.osm, sqlite=self.sqlite)
        
        
    