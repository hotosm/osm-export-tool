import logging
import sys
import uuid
import os
from django.test import TestCase
from django.utils import timezone
from unittest import skip

from unittest import skip

from ..overpass import Overpass

logger = logging.getLogger(__name__)

class TestOverpass(TestCase):
    
    def setUp(self,):
        self.url = 'http://localhost/interpreter'
        self.bbox = '6.25,-10.85,6.40,-10.62' # monrovia
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.osm = self.path + '/monrovia.osm'
        
    def test_print_query(self,):
        overpass = Overpass(osm=self.osm, bbox=self.bbox)
        overpass.print_query()
    
    @skip
    def test_run_query(self, ):
        """
        BBOX order: miny, minx, maxy, maxx
        
        All of Liberia: 3.9,-12.34,8.88,-6.15
        Monrovia: 6.25,-10.85,6.40,-10.62
        """
        overpass = Overpass(osm=self.osm, bbox=self.bbox)
        overpass.run_query()
        
        os.remove(self.osm)


    
    