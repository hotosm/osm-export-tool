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


class TestSQliteToShp(SimpleTestCase):
    
    def setUp(self, ):
        self.path = os.path.dirname(os.path.realpath(__file__))
    
    @patch('os.path.exists')
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen')
    def test_convert(self, popen, pipe, exists):
        sqlite = self.path + '/files/test.sqlite'
        shapefile= self.path + '/files/shp'
        cmd = "ogr2ogr -f 'ESRI Shapefile' {0} {1} -lco ENCODING=UTF-8".format(shapefile, sqlite)
        proc = Mock()
        exists.return_value = True
        popen.return_value = proc
        proc.communicate.return_value = (Mock(), Mock())
        proc.wait.return_value = 0
        # set zipped to False for testing
        s2s = SQliteToShp(sqlite=sqlite, shapefile=shapefile,
                          zipped=False, debug=True)
        out = s2s.convert()
        exists.assert_called_once_with(sqlite)
        popen.assert_called_once_with(cmd, shell=True, executable='/bin/bash',
                                stdout=pipe, stderr=pipe)
        self.assertEquals(out, shapefile)
    
    @patch('os.path.exists')
    @patch('shutil.rmtree')
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen')
    def test_zip_img_file(self, popen, pipe, rmtree, exists):
        sqlite = self.path + '/files/test.sqlite'
        shapefile = self.path + '/files/shp'
        zipfile = '/home/ubuntu/www/hotosm/utils/tests/files/shp.zip'
        zip_cmd = "zip -j -r {0} {1}".format(zipfile, shapefile)
        exists.return_value = True
        proc = Mock()
        popen.return_value = proc
        proc.communicate.return_value = (Mock(), Mock())
        proc.wait.return_value = 0
        s2s = SQliteToShp(sqlite=sqlite, shapefile=shapefile,
                          zipped=False, debug=True)
        result = s2s._zip_shape_dir()
        exists.assert_called_once_with(sqlite)
        # test subprocess getting called with correct command
        popen.assert_called_once_with(zip_cmd, shell=True, executable='/bin/bash',
                                stdout=pipe, stderr=pipe)
        rmtree.assert_called_once_with(shapefile)
        self.assertEquals(result, zipfile)
