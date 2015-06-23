import logging
import sys
import uuid
import os
from django.test import TestCase
from django.utils import timezone
from unittest import skip
import mock
from mock import patch, MagicMock, Mock


from unittest import skip

from ..overpass import Overpass

logger = logging.getLogger(__name__)

class TestOverpass(TestCase):
    
    def setUp(self,):
        self.url = 'http://localhost/interpreter'
        self.bbox = '6.25,-10.85,6.40,-10.62' # monrovia
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.osm = self.path + '/files/query.osm'
        self.query = '(node(6.25,-10.85,6.40,-10.62);<;);out body;'
        
    def test_get_query(self,):
        overpass = Overpass(osm=self.osm, bbox=self.bbox)
        q = overpass.get_query()
        self.assertIsNotNone(q)
        self.assertEquals(self.query, q)
    
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
        
        


    
    