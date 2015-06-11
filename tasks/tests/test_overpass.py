import overpy
import logging
import sys
import uuid
import os
from urllib2 import urlopen
from urllib2 import HTTPError
from django.test import TestCase
from django.contrib.gis.gdal import DataSource
from django.utils import timezone

from unittest import skip

from ..overpass import OSMParser

logger = logging.getLogger(__name__)

class TestOverpass(TestCase):
    
    def setUp(self,):
        #self.api = overpy.HOTOverpass()
        self.url = 'http://localhost/interpreter'
        pass
        
    
    def test_ql(self, ):
        """
        BBOX order: miny, minx, maxy, maxx
        
        All of Liberia: 3.9,-12.34,8.88,-6.15
        Monrovia: 6.25,-10.85,6.40,-10.62
        """
        
        query = """
                (
                    node(6.25,-10.85,6.40,-10.62);
                    way(6.25,-10.85,6.40,-10.62);
                    rel(6.25,-10.85,6.40,-10.62);
                );
                (._;>;);
                out;
             """
        logger.debug('Query started at: %s' % timezone.now())
        try:
            with open('test.osm', 'w') as fd:
                f = urlopen(self.url, query)
                for line in f.readlines():
                    fd.write(line)
                f.close()
            fd.close()
        except HTTPError as e:
            f = e
        logger.debug('Query finished at %s' % timezone.now())
        
        #parser = OSMParser('/home/ubuntu/www/hotosm/test.osm')
        #parser.create_initial_sqlite()
        
        

    
    