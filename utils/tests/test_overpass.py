import logging
import sys
import uuid
import os
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User, Group
from django.contrib.gis.geos import GEOSGeometry, Polygon
from unittest import skip
import mock
from mock import patch, MagicMock, Mock
from jobs.models import Job, ExportFormat, Tag

from unittest import skip

from ..overpass import Overpass
from jobs import presets


logger = logging.getLogger(__name__)

class TestOverpass(TestCase):
    
    def setUp(self,):
        self.url = 'http://localhost/interpreter'
        self.bbox = '6.25,-10.85,6.40,-10.62' # monrovia
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.formats = ExportFormat.objects.all() #pre-loaded by 'insert_export_formats' migration
        Group.objects.create(name='DefaultExportExtentGroup')
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
        self.query = '(node(6.25,-10.85,6.40,-10.62);<;);out body;'
        self.job.tags.all().delete()
        parser = presets.PresetParser(self.path + '/files/hdm_presets.xml')
        tags = parser.parse()
        self.assertIsNotNone(tags)
        self.assertEquals(238, len(tags))
        # save all the tags from the preset
        for tag_dict in tags:
            tag = Tag.objects.create(
                key = tag_dict['key'],
                value = tag_dict['value'],
                job = self.job,
                data_model = 'osm',
                geom_types = tag_dict['geom_types']
            )
        self.assertEquals(238, self.job.tags.all().count())
        
    def test_get_query(self,):
        overpass = Overpass(osm=self.osm, bbox=self.bbox, tags=self.job.filters)
        q = overpass.get_query()
        self.assertIsNotNone(q)
    
    @skip  
    def test_op_query_no_tags(self, ):
        op = Overpass(osm=self.osm, bbox=self.bbox)
        logger.debug(op.get_query())
        op.run_query()
    
    @skip
    def test_op_query_with_tags(self, ):
        op = Overpass(osm=self.osm, bbox=self.bbox, tags=self.job.filters)
        logger.debug(op.get_query())
        op.run_query()
    
    @skip
    def test_with_hdm_tags(self, ):
        parser = presets.PresetParser(preset=self.path + '/files/hdm_presets.xml')
        tags = parser.parse()
        filters = []
        for tag in tags:
            logger.debug(tag)
            filter_tag = '{0}:{1}'.format(tag['key'], tag['value'])
            filters.append(filter_tag)
        op = Overpass(osm=self.osm, bbox=self.bbox, tags=filters)
        op.run_query()
    
    @patch('utils.overpass.requests.post')
    def test_run_query(self, mock_post):
        op = Overpass(osm=self.osm, bbox=self.bbox)
        q = op.get_query()
        out = self.path + '/files/query.osm'
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
        
    
        
        


    
    