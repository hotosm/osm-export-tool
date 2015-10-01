# -*- coding: utf-8 -*-
import logging

from mock import Mock, patch

from django.test import SimpleTestCase

from ..pbf import OSMToPBF

logger = logging.getLogger(__name__)


class TestOSMToPBF(SimpleTestCase):

    @patch('os.path.exists')
    @patch('utils.garmin.subprocess.PIPE')
    @patch('utils.garmin.subprocess.Popen')
    def test_convert(self, popen, pipe, exists):
        osm = '/path/to/sample.osm'
        pbffile = '/path/to/sample.pbf'
        convert_cmd = 'osmconvert {0} --out-pbf >{1}'.format(osm, pbffile)
        proc = Mock()
        exists.return_value = True
        popen.return_value = proc
        proc.communicate.return_value = (Mock(), Mock())
        proc.wait.return_value = 0
        o2p = OSMToPBF(osm=osm, pbffile=pbffile)
        out = o2p.convert()
        exists.assert_called_once_with(osm)
        popen.assert_called_once_with(convert_cmd, shell=True, executable='/bin/bash',
                                stdout=pipe, stderr=pipe)
        self.assertEquals(out, pbffile)
