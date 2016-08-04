# -*- coding: utf-8 -*-
import logging
import os

from mock import Mock, patch

from django.conf import settings
from django.test import TestCase

from ..garmin import GarminConfigParser, OSMToIMG

logger = logging.getLogger(__name__)


class TestOSMToIMG(TestCase):
    """
    Test case to for garmin.OSMToIMG
    """

    def setUp(self,):
        #self.path = os.path.dirname(os.path.realpath(__file__))
        self.path = settings.ABS_PATH()
        # just for testing
        self.config = self.path + '/utils/tests/files/garmin_config.xml'
        self.work_dir = self.path + '/utils/tests/files/garmin'
        self.pbffile = self.path + '/utils/tests/files/query.pbf'

        #self.config = '/files/garmin_config.xml'
        #self.work_dir = '/files/garmin'
        #self.pbffile = '/files/query.pbf'
        self.region = "Indonesia, Sri Lanka, and Bangladesh"

    def test_config_parser(self,):
        parser = GarminConfigParser(self.config)
        params = parser.get_config()
        self.assertIsNotNone(params)
        mkgmap = params.get('mkgmap')
        splitter = params.get('splitter')
        self.assertEquals('/home/ubuntu/garmin/mkgmap/mkgmap.jar', mkgmap)
        self.assertEquals('/home/ubuntu/garmin/splitter/splitter.jar', splitter)

    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen')
    def test_convert(self, popen, pipe, mkdirs, exists):
        splitter_cmd = """
            java -Xmx1024m -jar /home/ubuntu/garmin/splitter/splitter.jar \
            --output-dir={0} \
            {1}""".format(self.work_dir, self.pbffile)
        # configure the mocks
        proc = Mock()
        popen.return_value = proc
        proc.communicate.return_value = (Mock(), Mock())
        proc.wait.return_value = 0
        exists.return_value = True
        o2i = OSMToIMG(
            pbffile=self.pbffile, work_dir=self.work_dir,
            config=self.config, region=self.region, debug=False
        )
        exists.assert_called_once_with(self.pbffile)
        o2i.run_splitter()
        # test subprocess getting called with correct command
        popen.assert_called_once_with(splitter_cmd, shell=True, executable='/bin/bash',
                                stdout=pipe, stderr=pipe)

    @patch('os.path.exists')
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen')
    def test_mkgmap(self, popen, pipe, exists):
        mkgmap_cmd = """
            java -Xmx1024m -jar /home/ubuntu/garmin/mkgmap/mkgmap.jar \
            --gmapsupp \
            --output-dir={0} \
            --description="HOT Export Garmin Map" \
            --mapname=80000111 \
            --family-name="HOT Exports" \
            --family-id="2" \
            --series-name="HOT Exports" \
            --region-name="Indonesia, Sri Lanka, and Bangladesh" \
            --index \
            --route \
            --generate-sea=extend-sea-sectors \
            --draw-priority=100 \
            --read-config={1}
        """.format(self.work_dir, self.work_dir + '/template.args')
        exists.return_value = True
        proc = Mock()
        popen.return_value = proc
        proc.communicate.return_value = (Mock(), Mock())
        proc.wait.return_value = 0
        # set zipped to False for testing
        o2i = OSMToIMG(
            pbffile=self.pbffile, work_dir=self.work_dir,
            config=self.config, zipped=False, region=self.region, debug=False
        )
        exists.assert_called_once_with(self.pbffile)
        imgfile = o2i.run_mkgmap()
        exists.assert_called_twice_with('/files/garmin/template.args')
        # test subprocess getting called with correct command
        popen.assert_called_once_with(mkgmap_cmd, shell=True, executable='/bin/bash',
                                stdout=pipe, stderr=pipe)
        proc.communicate.assert_called_once()
        proc.wait.assert_called_once()

        self.assertEquals(imgfile, self.work_dir + '/gmapsupp.img')

    @patch('os.path.exists')
    @patch('os.remove')
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen')
    def test_zip_img_file(self, popen, pipe, remove, exists):
        zipfile = self.path + '/utils/tests/files/garmin/garmin.zip'
        imgfile = self.path + '/utils/tests/files/garmin/gmapsupp.img'
        zip_cmd = "zip -j {0} {1}".format(zipfile, imgfile)
        exists.return_value = True
        proc = Mock()
        popen.return_value = proc
        proc.communicate.return_value = (Mock(), Mock())
        proc.wait.return_value = 0
        o2i = OSMToIMG(
            pbffile=self.pbffile, work_dir=self.work_dir,
            config=self.config, region=self.region, debug=False
        )
        exists.assert_called_once_with(self.pbffile)
        result = o2i._zip_img_file()
        # test subprocess getting called with correct command
        popen.assert_called_once_with(zip_cmd, shell=True, executable='/bin/bash',
                                stdout=pipe, stderr=pipe)
        proc.communicate.assert_called_once()
        proc.wait.assert_called_once()
        remove.assert_called_once_with(imgfile)
        self.assertEquals(result, zipfile)
