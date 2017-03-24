# -*- coding: utf-8 -*-
import logging
import os

from mock import Mock, patch

from django.conf import settings
from django.test import TransactionTestCase

from ..shp import GPKGToShp

logger = logging.getLogger(__name__)


class TestGPKGToShp(TransactionTestCase):

    def setUp(self, ):
        self.path = settings.ABS_PATH()

    @patch('os.path.exists')
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen')
    def test_convert(self, popen, pipe, exists):
        gpkg = os.path.join(self.path, '/utils/tests/files/test.gpkg')
        shapefile = os.path.join(self.path, '/utils/tests/files/shp')
        layer_name = os.path.splitext(os.path.basename(gpkg))[0]
        cmd = "ogr2ogr -f 'ESRI Shapefile' {0} {1} -lco ENCODING=UTF-8 -overwrite".format(shapefile, gpkg, layer_name)
        proc = Mock()
        exists.return_value = True
        popen.return_value = proc
        proc.communicate.return_value = (Mock(), Mock())
        proc.wait.return_value = 0
        # set zipped to False for testing
        s2s = GPKGToShp(gpkg=gpkg, shapefile=shapefile,
                          zipped=False, debug=False)
        out = s2s.convert()
        exists.assert_called_once_with(gpkg)
        popen.assert_called_once_with(cmd, shell=True, executable='/bin/bash',
                                stdout=pipe, stderr=pipe)
        self.assertEquals(out, shapefile)

    @patch('os.path.exists')
    @patch('shutil.rmtree')
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen')
    def test_zip_img_file(self, popen, pipe, rmtree, exists):
        gpkg = os.path.join(self.path, '/utils/tests/files/test.gpkg')
        shapefile = os.path.join(self.path, '/utils/tests/files/shp')
        zipfile = os.path.join(self.path, '/utils/tests/files/shp.zip')
        zip_cmd = "zip -j -r {0} {1}".format(zipfile, shapefile)
        exists.return_value = True
        proc = Mock()
        popen.return_value = proc
        proc.communicate.return_value = (Mock(), Mock())
        proc.wait.return_value = 0
        s2s = GPKGToShp(gpkg=gpkg, shapefile=shapefile,
                          zipped=False, debug=False)
        result = s2s._zip_shape_dir()
        exists.assert_called_once_with(gpkg)
        # test subprocess getting called with correct command
        popen.assert_called_once_with(zip_cmd, shell=True, executable='/bin/bash',
                                stdout=pipe, stderr=pipe)
        rmtree.assert_called_once_with(shapefile)
        self.assertEquals(result, zipfile)
