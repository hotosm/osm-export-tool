# -*- coding: utf-8 -*-
import logging

from mock import patch

from django.contrib.auth.models import Group, User
from django.contrib.gis.geos import GEOSGeometry, Polygon

from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from oet2.jobs.models import ExportFormat, Job

logger = logging.getLogger(__name__)


class TestJobFilter(APITestCase):

    def setUp(self,):
        Group.objects.create(name='TestDefaultExportExtentGroup')
        self.user1 = User.objects.create_user(
            username='demo1', email='demo@demo.com', password='demo'
        )
        self.user2 = User.objects.create_user(
            username='demo2', email='demo@demo.com', password='demo'
        )
        extents = (-3.9, 16.1, 7.0, 27.6)
        bbox = Polygon.from_bbox(extents)
        the_geom = GEOSGeometry(bbox, srid=4326)
        self.job1 = Job.objects.create(name='TestJob1',
                                 description='Test description', user=self.user1,
                                 the_geom=the_geom)
        self.job2 = Job.objects.create(name='TestJob2',
                                 description='Test description', user=self.user2,
                                 the_geom=the_geom)
        format = ExportFormat.objects.get(slug='obf')
        self.job1.formats.add(format)
        self.job2.formats.add(format)
        token = Token.objects.create(user=self.user1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key,
                                HTTP_ACCEPT='application/json; version=1.0',
                                HTTP_ACCEPT_LANGUAGE='en',
                                HTTP_HOST='testserver')

    @patch('api.views.ExportTaskRunner')
    def test_filterset_no_user(self, mock):
        task_runner = mock.return_value
        url = reverse('api:jobs-list')
        formats = [format.slug for format in ExportFormat.objects.all()]
        url += '?start=2015-01-01&end=2030-08-01'
        response = self.client.get(url)
        self.assertEquals(2, len(response.data))

    @patch('api.views.ExportTaskRunner')
    def test_filterset_with_user(self, mock):
        task_runner = mock.return_value
        url = reverse('api:jobs-list')
        formats = [format.slug for format in ExportFormat.objects.all()]
        url += '?start=2015-01-01&end=2030-08-01&user=demo1'
        response = self.client.get(url)
        self.assertEquals(1, len(response.data))
