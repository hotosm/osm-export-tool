# -*- coding: utf-8 -*-
import logging
import os

from mock import Mock, patch

from django.conf import settings
from django.test import TestCase

from ..osmand import OSMToOBF, UpdateBatchXML

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


class TestOSMToOBF(TestCase):
    """
    Test case to test generation of OBF files.
    Depends on install of OsmAndMapCreator
    so skipping for general run of tests.
    """

    def setUp(self,):
        #self.path = os.path.dirname(os.path.realpath(__file__))
        self.path = settings.ABS_PATH()
        # just for testing
        self.map_creator_dir = settings.OSMAND_MAP_CREATOR_DIR
        self.work_dir = self.path + '/utils/tests/files'
        self.pbffile = self.path + '/utils/tests/files/query.pbf'

    @patch('os.path.exists')
    @patch('shutil.copy')
    @patch('os.listdir')
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen')
    def test_create_obf(self, popen, pipe, listdir, copy, exists):
        obf_cmd = """
            cd /home/ubuntu/osmand/OsmAndMapCreator && \
            java -Djava.util.logging.config.file=logging.properties \
                -Xms256M -Xmx1024M -cp "./OsmAndMapCreator.jar:./lib/OsmAnd-core.jar:./lib/*.jar" \
                net.osmand.data.index.IndexBatchCreator {0}
        """.format(self.work_dir + '/batch.xml')
        exists.return_value = True
        proc = Mock()
        popen.return_value = proc
        proc.communicate.return_value = (Mock(), Mock())
        proc.wait.return_value = 0
        listdir.return_value = ['query.obf']
        o2o = OSMToOBF(
            pbffile=self.pbffile, work_dir=self.work_dir,
            map_creator_dir=self.map_creator_dir, debug=False
        )
        obffile = o2o.convert()
        exists.assert_called_twice_with(self.work_dir + '/query.osm.pbf')
        exists.assert_called_twice_with(self.work_dir)
        copy.assert_called_once_with(self.pbffile, self.work_dir + '/query.osm.pbf')
        popen.assert_called_once_with(obf_cmd, shell=True, executable='/bin/bash',
                                stdout=pipe, stderr=pipe)
        proc.communicate.assert_called_once()
        proc.wait.assert_called_once()
        listdir.assert_called_once_with(self.work_dir)
        self.assertEquals(obffile, self.work_dir + '/query.obf')
