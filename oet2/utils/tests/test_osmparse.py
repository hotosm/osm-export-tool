# -*- coding: utf-8 -*-

from mock import MagicMock, Mock, patch

from django.conf import settings
from django.test import TestCase

from ..osmparse import OSMParser


class TestOSMParser(TestCase):

    def setUp(self,):
        self.path = settings.ABS_PATH()

    @patch('os.path.exists')
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen')
    def test_create_spatialite(self, popen, pipe, exists):
        ogr_cmd = """
            ogr2ogr -f SQlite -dsco SPATIALITE=YES /path/to/query.sqlite /path/to/query.pbf \
            --config OSM_CONFIG_FILE {0} \
            --config OGR_INTERLEAVED_READING YES \
            --config OSM_MAX_TMPFILE_SIZE 100 -gt 65536
        """.format(self.path + '/utils/conf/hotosm.ini')
        exists.return_value = True
        proc = Mock()
        popen.return_value = proc
        proc.communicate.return_value = (Mock(), Mock())
        proc.wait.return_value = 0
        parser = OSMParser(osm='/path/to/query.pbf', sqlite='/path/to/query.sqlite')
        exists.assert_called_twice_with('/path/to/query.pbf')
        parser.create_spatialite()
        popen.assert_called_once_with(ogr_cmd, shell=True, executable='/bin/bash',
                                stdout=pipe, stderr=pipe)
        proc.communicate.assert_called_once()
        proc.wait.assert_called_once()

    @patch('os.path.exists')
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen')
    def test_create_default_schema(self, popen, pipe, exists):
        sql_cmd = "spatialite /path/to/query.sqlite < {0}".format(self.path + '/utils/sql/planet_osm_schema.sql')
        proc = Mock()
        popen.return_value = proc
        proc.communicate.return_value = (Mock(), Mock())
        proc.wait.return_value = 0
        exists.return_value = True
        parser = OSMParser(osm='/path/to/query.pbf', sqlite='/path/to/query.sqlite')
        parser.create_default_schema()
        exists.assert_called_twice_with('/path/to/query.sqlite')
        popen.assert_called_once_with(sql_cmd, shell=True, executable='/bin/bash',
                                stdout=pipe, stderr=pipe)
        proc.communicate.assert_called_once()
        proc.wait.assert_called_once()

    @patch('utils.osmparse.ogr.Open')
    @patch('os.path.exists')
    def test_update_zindexes(self, exists, ogr_open):
        exists.return_value = True
        ogr_ds = MagicMock()
        ogr_ds.GetLayerCount.return_value = 3
        ogr_ds.ExecuteSQL = MagicMock()
        ogr_ds.Destroy = MagicMock()
        ogr_open.return_value = ogr_ds
        parser = OSMParser(osm='/path/to/query.pbf', sqlite='/path/to/query.sqlite')
        parser.update_zindexes()
        exists.assert_called_twice_with('/path/to/query.sqlite')
        ogr_open.assert_called_once_with('/path/to/query.sqlite', update=True)
        self.assertEquals(30, ogr_ds.ExecuteSQL.call_count)
        ogr_ds.Destroy.assert_called_once()
