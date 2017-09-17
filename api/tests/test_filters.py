# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.contrib.gis.geos import GEOSGeometry, Polygon

from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from jobs.models import Job, SavedFeatureSelection


class TestJobFilter(APITestCase):
    def setUp(self,):
        user1 = User.objects.create_user(username='demo1')
        user2 = User.objects.create_user(username='demo2')
        #minx, miny, maxx, maxy
        bbox1 = GEOSGeometry(Polygon.from_bbox([1.0, 1.0, 2.0, 2.0]), srid=4326)
        bbox2 = GEOSGeometry(Polygon.from_bbox([10.0, 10.0, 11.0, 11.0]), srid=4326)
        self.job1 = Job.objects.create(
            name='MyPrivateJob',
            export_formats=["shp"],
            user=user1,
            the_geom=bbox1,
            published=False
        )
        self.job2 = Job.objects.create(
            name='TheirPublicJob',
            export_formats=["shp"],
            user=user2,
            the_geom=bbox2,
            published=True
        )
        self.job3 = Job.objects.create(
            name='TheirPrivateJob',
            export_formats=["shp"],
            user=user2,
            the_geom=bbox1,
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
        response = self.client.get(url + '?all=true')
        self.assertEquals(1, len(response.data['results']))
        self.assertEquals('TheirPublicJob', response.data['results'][0]['name'])

    def test_filterset_authenticated_unpublished(self):
        url = reverse('api:jobs-list')
        response = self.client.get(url + '?all=true')
        self.assertEquals(2, len(response.data['results']))
        self.assertEquals('TheirPublicJob', response.data['results'][0]['name'])
        self.assertEquals('MyPrivateJob', response.data['results'][1]['name'])

    def test_filterset_search_ownuser(self):
        url = reverse('api:jobs-list')
        url += '?mineonly=True'
        response = self.client.get(url)
        self.assertEquals(1, len(response.data['results']))
        self.assertEquals('MyPrivateJob', response.data['results'][0]['name'])

    def test_filterset_search_keyword(self):
        url = reverse('api:jobs-list')
        response = self.client.get(url + '?search=TheirPub&all=true')
        self.assertEquals(1, len(response.data['results']))
        self.assertEquals('TheirPublicJob', response.data['results'][0]['name'])
        response = self.client.get(url + '?search=nothing&all=true')
        self.assertEquals(0, len(response.data['results']))

    def test_search_jobs_by_date(self):
        self.job1.created_at = '2017-06-05T00:00:00Z'
        self.job1.save()
        self.job2.created_at = '2017-06-10T00:00:00Z'
        self.job2.save()

        url = reverse('api:jobs-list')
        response = self.client.get(url + '?before=2017-06-07T00:00:00Z&all=true')
        self.assertEquals(1, len(response.data['results']))
        self.assertEquals('MyPrivateJob', response.data['results'][0]['name'])

        response = self.client.get(url + '?after=2017-06-09T00:00:00Z&all=true')
        self.assertEquals(1, len(response.data['results']))
        self.assertEquals('TheirPublicJob', response.data['results'][0]['name'])

        response = self.client.get(url + '?after=2017-06-07T00:00:00Z&before=2017-06-09T00:00:00Z&all=true')
        self.assertEquals(0, len(response.data['results']))

    def test_search_jobs_by_bbox(self):
        url = reverse('api:jobs-list')
        response = self.client.get(url + "?bbox=0.0,0.0,2.0,2.0")
        self.assertEquals(1, len(response.data['results']))
        self.assertEquals('MyPrivateJob', response.data['results'][0]['name'])

    def test_search_jobs_by_bbox_invalid(self):
        url = reverse('api:jobs-list')
        response = self.client.get(url + "?bbox=")
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertTrue('bbox' in response.data)
        url = reverse('api:jobs-list')
        response = self.client.get(url + "?bbox=0.0,0.0")
        self.assertTrue('bbox' in response.data)


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
        response = self.client.get(url + '?all=true')
        self.assertEquals(1, len(response.data['results']))
        self.assertEquals('theirPublicConf', response.data['results'][0]['name'])

    def test_filterset_authenticated_private(self):
        url = reverse('api:configurations-list')
        response = self.client.get(url + '?all=true')
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
        response = self.client.get(url + '?search=theirPublic&all=true')
        self.assertEquals(1, len(response.data['results']))
        self.assertEquals('theirPublicConf', response.data['results'][0]['name'])
        response = self.client.get(url + '?search=nothing')
        self.assertEquals(0, len(response.data['results']))


# filter hdx by name, dataset prefix?
