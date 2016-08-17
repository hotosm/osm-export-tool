# -*- coding: utf-8 -*-
import logging
import os

from mock import Mock, patch

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.contrib.gis.geos import GEOSGeometry, Polygon
from django.test import TestCase

import oet2.jobs.presets as presets
from oet2.jobs.models import Job, Tag

from ..thematic_shp import ThematicSQliteToShp

logger = logging.getLogger(__name__)


class TestThematicShp(TestCase):

    def setUp(self,):
        self.path = settings.ABS_PATH()
        parser = presets.PresetParser(self.path + '/utils/tests/files/hdm_presets.xml')
        self.tags = parser.parse()
        Group.objects.create(name='TestDefaultExportExtentGroup')
        self.user = User.objects.create(username='demo', email='demo@demo.com', password='demo')
        bbox = Polygon.from_bbox((-7.96, 22.6, -8.14, 27.12))
        the_geom = GEOSGeometry(bbox, srid=4326)
        self.job = Job.objects.create(name='TestJob',
                                 description='Test description', event='Nepal activation',
                                 user=self.user, the_geom=the_geom)
        tags_dict = parser.parse()
        for entry in self.tags:
            tag = Tag.objects.create(
                name=entry['name'],
                key=entry['key'],
                value=entry['value'],
                geom_types=entry['geom_types'],
                data_model='PRESET',
                job=self.job
            )

    @patch('shutil.copy')
    @patch('os.path.exists')
    def testInit(self, exists, copy):
        sqlite = self.path + '/utils/tests/files/test.sqlite'
        shapefile = self.path + '/utils/tests/files/thematic_shp'
        cmd = "ogr2ogr -f 'ESRI Shapefile' {0} {1} -lco ENCODING=UTF-8".format(shapefile, sqlite)
        proc = Mock()
        exists.return_value = True
        # set zipped to False for testing
        t2s = ThematicSQliteToShp(
            sqlite=sqlite, shapefile=shapefile,
            tags=None, job_name='test_thematic_shp',
            zipped=False, debug=False
        )
        exists.assert_called_twice()
        copy.assert_called_once()

    @patch('shutil.copy')
    @patch('os.path.exists')
    @patch('sqlite3.connect')
    def test_generate_thematic_schema(self, connect, exists, copy):
        sqlite = self.path + '/utils/tests/files/test.sqlite'
        shapefile = self.path + '/utils/tests/files/thematic_shp'
        thematic_sqlite = self.path + '/utils/tests/files/test_thematic_shp_thematic.sqlite'
        exists.return_value = True
        conn = Mock()
        conn.enable_load_extention = Mock()
        connect.return_value = conn
        cur = Mock()
        conn.cursor = cur
        cur.execute = Mock()
        cmd = "SELECT load_extension('libspatialite')"
        tags = self.job.categorised_tags
        t2s = ThematicSQliteToShp(
            sqlite=sqlite, shapefile=shapefile,
            tags=tags, job_name='test_thematic_shp',
            zipped=False, debug=False
        )
        exists.assert_called_twice()
        copy.assert_called_once()
        t2s.generate_thematic_schema()
        connect.assert_called_once()
        conn.load_extention.assert_called_once()
        conn.cursor.assert_called_once()
        # cur.execute.assert_called_with(cmd)

    @patch('shutil.copy')
    @patch('os.path.exists')
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen')
    @patch('sqlite3.connect')
    def test_convert(self, connect, popen, pipe, exists, copy):
        sqlite = self.path + '/utils/tests/files/test_thematic_shp_thematic.sqlite'
        shapefile = self.path + '/utils/tests/files/shp'
        cmd = "ogr2ogr -f 'ESRI Shapefile' {0} {1} -lco ENCODING=UTF-8".format(shapefile, sqlite)
        proc = Mock()
        exists.return_value = True
        conn = Mock()
        conn.enable_load_extention = Mock()
        connect.return_value = conn
        cur = Mock()
        conn.cursor = cur
        cur.execute = Mock()
        popen.return_value = proc
        proc.communicate.return_value = (Mock(), Mock())
        proc.wait.return_value = 0
        # set zipped to False for testing
        tags = self.job.categorised_tags
        t2s = ThematicSQliteToShp(
            sqlite=sqlite, shapefile=shapefile,
            tags=tags, job_name='test_thematic_shp',
            zipped=False, debug=False
        )
        exists.assert_called_twice()
        copy.assert_called_once()
        out = t2s.convert()
        popen.assert_called_once_with(cmd, shell=True, executable='/bin/bash',
                                stdout=pipe, stderr=pipe)
        self.assertEquals(out, shapefile)

    @patch('shutil.copy')
    @patch('os.path.exists')
    @patch('shutil.rmtree')
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen')
    def test_zip_shp_file(self, popen, pipe, rmtree, exists, copy):
        sqlite = self.path + '/utils/tests/files/test_thematic_shp_thematic.sqlite'
        shapefile = self.path + '/utils/tests/files/thematic_shp'
        zipfile = self.path + '/utils/tests/files/thematic_shp.zip'
        zip_cmd = "zip -j -r {0} {1}".format(zipfile, shapefile)
        exists.return_value = True
        proc = Mock()
        popen.return_value = proc
        proc.communicate.return_value = (Mock(), Mock())
        proc.wait.return_value = 0
        tags = self.job.categorised_tags
        t2s = ThematicSQliteToShp(
            sqlite=sqlite, shapefile=shapefile,
            tags=tags, job_name='test_thematic_shp',
            zipped=False, debug=False
        )
        exists.assert_called_twice()
        copy.assert_called_once()
        result = t2s._zip_shape_dir()
        # test subprocess getting called with correct command
        popen.assert_called_once_with(zip_cmd, shell=True, executable='/bin/bash',
                                stdout=pipe, stderr=pipe)
        rmtree.assert_called_once_with(shapefile)
        self.assertEquals(result, zipfile)
