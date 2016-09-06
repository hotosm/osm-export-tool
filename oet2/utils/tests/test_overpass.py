# -*- coding: utf-8 -*-
import logging
import os
from unittest import skip

import mock
from mock import patch

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.contrib.gis.geos import GEOSGeometry, Polygon
from django.test import TestCase

from oet2.jobs import presets
from oet2.jobs.models import ExportFormat, Job, Tag

from ..overpass import Overpass

logger = logging.getLogger(__name__)


class TestOverpass(TestCase):

    def setUp(self,):
        self.url = 'http://localhost/interpreter'
        self.bbox = '6.25,-10.85,6.40,-10.62'  # monrovia
        self.path = settings.ABS_PATH()
        self.formats = ExportFormat.objects.all()  # pre-loaded by 'insert_export_formats' migration
        Group.objects.create(name='TestDefaultExportExtentGroup')
        self.user = User.objects.create(username='demo', email='demo@demo.com', password='demo')
        bbox = Polygon.from_bbox((-7.96, 22.6, -8.14, 27.12))
        the_geom = GEOSGeometry(bbox, srid=4326)
        self.job = Job.objects.create(name='TestJob',
                                 description='Test description', event='Nepal activation',
                                 user=self.user, the_geom=the_geom)
        self.uid = self.job.uid
        # add the formats to the job
        self.job.formats = self.formats
        self.job.save()
        self.osm = self.path + '/files/query.osm'
        self.query = '[maxsize:2147483648][timeout:1600];(node(6.25,-10.85,6.40,-10.62);<;);out body;'
        self.job.tags.all().delete()
        parser = presets.PresetParser(self.path + '/utils/tests/files/hdm_presets.xml')
        tags = parser.parse()
        self.assertIsNotNone(tags)
        self.assertEquals(256, len(tags))
        # save all the tags from the preset
        for tag_dict in tags:
            tag = Tag.objects.create(
                key=tag_dict['key'],
                value=tag_dict['value'],
                job=self.job,
                data_model='osm',
                geom_types=tag_dict['geom_types']
            )
        self.assertEquals(256, self.job.tags.all().count())

    def test_get_query(self,):
        overpass = Overpass(
            stage_dir=self.path + '/utils/tests/files/',
            bbox=self.bbox, job_name='testjob',
            filters=self.job.filters
        )
        q = overpass.get_query()
        self.assertEquals(q, self.query)

    @patch('utils.overpass.requests.post')
    def test_run_query(self, mock_post):
        op = Overpass(
            stage_dir=self.path + '/utils/tests/files/',
            bbox=self.bbox, job_name='testjob',
            filters=self.job.filters
        )
        q = op.get_query()
        out = self.path + '/utils/tests/files/query.osm'
        mock_response = mock.Mock()
        expected = ['<osm>some data</osm>']
        mock_response.iter_content.return_value = expected
        mock_post.return_value = mock_response
        op.run_query()
        mock_post.assert_called_once_with(self.url,
                                              data=q,
                                              stream=True)
        f = open(out)
        data = f.read()
        self.assertEqual(data, expected[0])
        f.close()
        os.remove(out)
