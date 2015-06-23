import logging
import sys
import uuid
import os
from django.test import SimpleTestCase
from django.utils import timezone
from django.core.files import File
from unittest import skip
import mock
from mock import patch, Mock

from ..shp import SQliteToShp

logger = logging.getLogger(__name__)


class TestSQlliteToShp(SimpleTestCase):
    
    def setUp(self, ):
        self.path = os.path.dirname(os.path.realpath(__file__))
    
    @patch('utils.garmin.subprocess.PIPE')
    @patch('utils.garmin.subprocess.Popen')
    def test_convert(self, popen, pipe):
        sqlite = self.path + '/files/test.sqlite'
        shapefile= self.path + '/files/shp'
        cmd = "ogr2ogr -f 'ESRI Shapefile' {0} {1} -lco ENCODING=UTF-8".format(shapefile, sqlite)
        proc = Mock()
        popen.return_value = proc
        proc.communicate.return_value = (Mock(), Mock())
        proc.wait.return_value = 0
        # set zipped to False for testing
        s2s = SQliteToShp(sqlite=sqlite, shapefile=shapefile,
                          zipped=False, debug=True)
        out = s2s.convert()
        popen.assert_called_once_with(cmd, shell=True, executable='/bin/bash',
                                stdout=pipe, stderr=pipe)
        self.assertEquals(out, shapefile)
    
    @patch('shutil.rmtree')
    @patch('utils.garmin.subprocess.PIPE')
    @patch('utils.garmin.subprocess.Popen')
    def test_zip_img_file(self, popen, pipe, rmtree):
        sqlite = self.path + '/files/test.sqlite'
        shapefile = self.path + '/files/shp'
        zipfile = '/home/ubuntu/www/hotosm/utils/tests/files/shp.zip'
        zip_cmd = "zip -r {0} {1}".format(zipfile, shapefile)
        proc = Mock()
        popen.return_value = proc
        proc.communicate.return_value = (Mock(), Mock())
        proc.wait.return_value = 0
        s2s = SQliteToShp(sqlite=sqlite, shapefile=shapefile,
                          zipped=False, debug=True)
        result = s2s._zip_shape_dir()
        # test subprocess getting called with correct command
        popen.assert_called_once_with(zip_cmd, shell=True, executable='/bin/bash',
                                stdout=pipe, stderr=pipe)
        rmtree.assert_called_once_with(shapefile)
        self.assertEquals(result, zipfile)

