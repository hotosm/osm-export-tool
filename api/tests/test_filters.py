# -*- coding: utf-8 -*-
from unittest import skip

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.contrib.gis.geos import GEOSGeometry, Polygon

from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from jobs.models import Job, SavedFeatureSelection


class TestJobFilter(APITestCase):
    def setUp(self,):
        user1 = User.objects.create_user(username='demo1')
        user2 = User.objects.create_user(username='demo2')
        extents = (-3.9, 16.1, 7.0, 27.6)
        bbox = Polygon.from_bbox(extents)
        the_geom = GEOSGeometry(bbox, srid=4326)
        Job.objects.create(
            name='MyPrivateJob',
            export_formats=["shp"],
            user=user1,
            the_geom=the_geom,
            published=False
        )
        Job.objects.create(
            name='TheirPublicJob',
            export_formats=["shp"],
            user=user2,
            the_geom=the_geom,
            published=True
        )
        Job.objects.create(
            name='TheirPrivateJob',
            export_formats=["shp"],
            user=user2,
            the_geom=the_geom,
            published=False
        )
        token = Token.objects.create(user=user1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key,
                                HTTP_ACCEPT='application/json; version=1.0',
                                HTTP_ACCEPT_LANGUAGE='en',
                                HTTP_HOST='testserver')

    def test_filterset_unauthenticated(self):
        url = reverse('api:jobs-list')
        self.client.credentials(HTTP_ACCEPT='application/json; version=1.0',
                                HTTP_ACCEPT_LANGUAGE='en',
                                HTTP_HOST='testserver')
        response = self.client.get(url)
        self.assertEquals(1, len(response.data['results']))
        self.assertEquals('TheirPublicJob', response.data['results'][0]['name'])

    def test_filterset_authenticated_unpublished(self):
        url = reverse('api:jobs-list')
        response = self.client.get(url)
        self.assertEquals(2, len(response.data['results']))
        self.assertEquals('MyPrivateJob', response.data['results'][0]['name'])
        self.assertEquals('TheirPublicJob', response.data['results'][1]['name'])

    def test_filterset_search_ownuser(self):
        url = reverse('api:jobs-list')
        url += '?mineonly=True'
        response = self.client.get(url)
        self.assertEquals(1, len(response.data['results']))
        self.assertEquals('MyPrivateJob', response.data['results'][0]['name'])

    def test_filterset_search_keyword(self):
        url = reverse('api:jobs-list')
        response = self.client.get(url + '?search=TheirPub')
        self.assertEquals(1, len(response.data['results']))
        self.assertEquals('TheirPublicJob', response.data['results'][0]['name'])
        response = self.client.get(url + '?search=nothing')
        self.assertEquals(0, len(response.data['results']))

    @skip('')
    def test_search_jobs_by_date(self):
        pass

    @skip('')
    def test_search_jobs_by_bbox(Self):
        pass


class TestConfigurationFilter(APITestCase):
    def setUp(self,):
        user1 = User.objects.create_user(username='demo1')
        user2 = User.objects.create_user(username='demo2')
        SavedFeatureSelection.objects.create(
            name='myPrivateConf',
            description="description one",
            user=user1,
            public=False
        )
        SavedFeatureSelection.objects.create(
            name='theirPublicConf',
            description="description two",
            user=user2,
            public=True
        )
        SavedFeatureSelection.objects.create(
            name='theirPrivateConf',
            description="description three",
            user=user2,
            public=False
        )
        SavedFeatureSelection.objects.create(
            name='deletedConf',
            description="description three",
            user=user1,
            public=True,
            deleted=True
        )
        token = Token.objects.create(user=user1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key,
                                HTTP_ACCEPT='application/json; version=1.0',
                                HTTP_ACCEPT_LANGUAGE='en',
                                HTTP_HOST='testserver')

    def test_filterset_unauthenticated(self):
        url = reverse('api:configurations-list')
        self.client.credentials(HTTP_ACCEPT='application/json; version=1.0',
                                HTTP_ACCEPT_LANGUAGE='en',
                                HTTP_HOST='testserver')
        response = self.client.get(url)
        self.assertEquals(1, len(response.data['results']))
        self.assertEquals('theirPublicConf', response.data['results'][0]['name'])

    def test_filterset_authenticated_private(self):
        url = reverse('api:configurations-list')
        response = self.client.get(url)
        self.assertEquals(2, len(response.data['results']))
        self.assertEquals('myPrivateConf', response.data['results'][0]['name'])
        self.assertEquals('theirPublicConf', response.data['results'][1]['name'])

    def test_filterset_search_ownuser(self):
        url = reverse('api:configurations-list')
        url += '?mineonly=True'
        response = self.client.get(url)
        self.assertEquals(1, len(response.data['results']))
        self.assertEquals('myPrivateConf', response.data['results'][0]['name'])

    def test_filterset_search_keyword(self):
        url = reverse('api:configurations-list')
        response = self.client.get(url + '?search=theirPublic')
        self.assertEquals(1, len(response.data['results']))
        self.assertEquals('theirPublicConf', response.data['results'][0]['name'])
        response = self.client.get(url + '?search=nothing')
        self.assertEquals(0, len(response.data['results']))


# filter hdx by name, dataset prefix?

class TestBBoxSearch(APITestCase):
    """
    Test cases for testing bounding box searches.
    """
    def setUp(self, mock):
        url = reverse('api:jobs-list')
        # create dummy user
        self.user = User.objects.create_user(
            username='demo', email='demo@demo.com', password='demo'
        )
        # setup token authentication
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key,
                                HTTP_ACCEPT='application/json; version=1.0',
                                HTTP_ACCEPT_LANGUAGE='en',
                                HTTP_HOST='testserver')
        # pull out the formats
        # create test jobs
        extents = [(-3.9, 16.1, 7.0, 27.6), (36.90, 13.54, 48.52, 20.24),
            (-71.79, -49.57, -67.14, -46.16), (-61.27, -6.49, -56.20, -2.25),
            (-11.61, 32.07, -6.42, 36.31), (-10.66, 5.81, -2.45, 11.83),
            (47.26, 34.58, 52.92, 39.15), (90.00, 11.28, 95.74, 17.02)]
        for extent in extents:
            request_data = {
                'name': 'TestJob',
                'description': 'Test description',
                'event': 'Test Activation',
                'xmin': extent[0],
                'ymin': extent[1],
                'xmax': extent[2],
                'ymax': extent[3],
                'formats': []
            }
            response = self.client.post(url, request_data, format='json')
            self.assertEquals(status.HTTP_202_ACCEPTED, response.status_code)
        self.assertEquals(8, len(Job.objects.all()))
        LinkHeaderPagination.page_size = 2

    @skip('')
    def test_bbox_search_success(self, ):
        url = reverse('api:jobs-list')
        extent = (-79.5, -16.16, 7.40, 52.44)
        param = 'bbox={0},{1},{2},{3}'.format(extent[0], extent[1], extent[2], extent[3])
        response = self.client.get('{0}?{1}'.format(url, param))
        self.assertEquals(status.HTTP_206_PARTIAL_CONTENT, response.status_code)
        self.assertEquals(2, len(response.data))  # 8 jobs in total but response is paginated

    @skip('')
    def test_list_jobs_no_bbox(self, ):
        url = reverse('api:jobs-list')
        response = self.client.get(url)
        self.assertEquals(status.HTTP_206_PARTIAL_CONTENT, response.status_code)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        self.assertEquals(response['Link'], '<http://testserver/api/jobs?page=2>; rel="next"')
        self.assertEquals(2, len(response.data))  # 8 jobs in total but response is paginated

    @skip('')
    def test_bbox_search_missing_params(self, ):
        url = reverse('api:jobs-list')
        param = 'bbox='  # missing params
        response = self.client.get('{0}?{1}'.format(url, param))
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        self.assertEquals('missing_bbox_parameter', response.data['id'])

    @skip('')
    def test_bbox_missing_coord(self, ):
        url = reverse('api:jobs-list')
        extent = (-79.5, -16.16, 7.40)  # one missing
        param = 'bbox={0},{1},{2}'.format(extent[0], extent[1], extent[2])
        response = self.client.get('{0}?{1}'.format(url, param))
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        self.assertEquals('missing_bbox_parameter', response.data['id'])
