import logging
import sys
import uuid
import os
from django.test import SimpleTestCase
from django.utils import timezone
from django.core.files import File
from unittest import skip

from ..pbf import OSMToPBF

logger = logging.getLogger(__name__)


class TestOSMToPBF(SimpleTestCase):
    
    def setUp(self, ):
        self.path = os.path.dirname(os.path.realpath(__file__))
    
    
    def test_convert(self, ):
        osm = self.path + '/sample.osm'
        pbf = self.path + '/sample.pbf'
        o2p = OSMToPBF(osm=osm, pbf=pbf)
        o2p.convert()
        f = None
        try:
            f = File(open(self.path + '/sample.pbf'))
            self.assertIsNotNone(f)
        except IOError as e:
            logger.debug(e)
        finally:
            f.close()
            os.remove(pbf)
        
