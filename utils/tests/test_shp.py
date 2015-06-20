import logging
import sys
import uuid
import os
from django.test import SimpleTestCase
from django.utils import timezone
from django.core.files import File
from unittest import skip

from ..shp import SQliteToShp

logger = logging.getLogger(__name__)


class TestSQlliteToShp(SimpleTestCase):
    
    def setUp(self, ):
        self.path = os.path.dirname(os.path.realpath(__file__))
    
    
    def test_convert(self, ):
        sqlite = self.path + '/test.sqlite'
        shapefile= self.path + '/test.shp'
        s2s = SQliteToShp(sqlite=sqlite, shapefile=shapefile, debug=True)
        s2s.convert()
        f = None
        try:
            f = File(open(self.path + '/test.shp'))
            self.assertIsNotNone(f)
        except IOError as e:
            logger.debug(e)
        finally:
            f.close()
            #os.remove(shapefile)
        
