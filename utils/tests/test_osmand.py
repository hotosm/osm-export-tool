import os
import logging
import shutil
from hot_exports import settings
from django.test import TestCase
from django.utils import timezone
from StringIO import StringIO
from unittest import skip

from ..osmand import UpdateBatchXML, OSMToOBF

logger = logging.getLogger(__name__)

class TestUpdateBatchXML(TestCase):
    
    def setUp(self,):
        self.path = os.path.dirname(os.path.realpath(__file__))
        
    def test_update_batch_xml(self, ):
        batch_xml = self.path + '/files/batch.xml'
        batch_update = UpdateBatchXML(batch_xml=batch_xml, work_dir=self.path)
        updated_file = batch_update.update()
        self.assertIsNotNone(updated_file)
        self.assertTrue(os.path.exists(updated_file))
        os.remove(updated_file)

@skip('Only for development purposes.')
class TestOSMToOBF(TestCase):
    """
    Test case to test generation of OBF files.
    Depends on install of OsmAndMapCreator
    so skipping for general run of tests.
    """
    
    def setUp(self,):
        self.path = os.path.dirname(os.path.realpath(__file__))
        # just for testing
        self.map_creator_dir = settings.OSMAND_MAP_CREATOR_DIR
        self.work_dir = self.path + '/files/osmand'
        self.pbffile = self.path + '/files/query.pbf'
        
    def test_create_obf(self,):
        o2o = OSMToOBF(
            pbffile=self.pbffile, work_dir=self.work_dir,
            map_creator_dir=self.map_creator_dir, debug=True
        )
        obffile = o2o.convert()
        self.assertTrue(os.path.exists(obffile))
        # cleanup
        shutil.rmtree(self.work_dir)
        
        



