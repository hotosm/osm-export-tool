# -*- coding: utf-8 -*-
import json
import os
import uuid
from unittest import skip

from mock import patch

from django.conf import settings
from django.contrib.auth.models import Group, User, Permission
from django.contrib.gis.geos import GEOSGeometry, Polygon
from django.contrib.contenttypes.models import ContentType
from django.core.files import File

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from api.pagination import LinkHeaderPagination
from jobs.models import Job, HDXExportRegion
from tasks.models import ExportRun, ExportTask
from feature_selection.feature_selection import FeatureSelection


class TestJobViewSet(APITestCase):

    def setUp(self, ):
        self.user = User.objects.create_user(
            username='demo', email='demo@demo.com', password='demo'
        )
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key,
                                HTTP_ACCEPT='application/json; version=1.0',
                                HTTP_ACCEPT_LANGUAGE='en',
                                HTTP_HOST='testserver')
        self.request_data = {
            'name': 'TestJob',
            'description': 'Test description',
            'event': 'Test Activation',
            'export_formats': ["shp"],
            'published': True,
            'the_geom':{'type':'Polygon','coordinates':[[[-17.464,14.727],[-17.449,14.727],[-17.449,14.740],[-17.464,14.740],[-17.464,14.727]]]},
            'feature_selection':FeatureSelection.example_raw("simple")
        }

    @skip("test the representation of export")
    def test_list(self, ):
        expected = '/api/jobs'
        url = reverse('api:jobs-list')
        self.assertEquals(expected, url)

    @patch('api.views.ExportTaskRunner')
    def test_create_job_success(self, mock):
        task_runner = mock.return_value
        url = reverse('api:jobs-list')
        response = self.client.post(url, self.request_data, format='json')
        job_uid = response.data['uid']
        task_runner.run_task.assert_called_once_with(job_uid=job_uid)

        # test the response headers
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')

        # test significant response content
        self.assertEqual(response.data['name'], self.request_data['name'])
        self.assertEqual(response.data['description'], self.request_data['description'])
        self.assertTrue(response.data['published'])

        j = Job.objects.get(uid=job_uid)
        self.assertFalse(j.hidden)
        self.assertFalse(j.unlimited_extent)


    @patch('api.views.ExportTaskRunner')
    def test_delete_disabled(self, mock):
        url = reverse('api:jobs-list')
        response = self.client.post(url, self.request_data, format='json')
        job_uid = response.data['uid']
        url = reverse('api:jobs-detail', args=[job_uid])
        response = self.client.delete(url)
        self.assertEquals(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_missing_the_geom(self, ):
        url = reverse('api:jobs-list')
        del self.request_data['the_geom']
        response = self.client.post(url, self.request_data,format='json')
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(['This field is required.'], response.data['the_geom'])

    def test_malformed_geojson_extent(self):
        url = reverse('api:jobs-list')
        self.request_data['the_geom'] = {'type':'Polygon','coordinates':[]}
        response = self.client.post(url, self.request_data,format='json')
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_toolarge_geojson_extent(self):
        url = reverse('api:jobs-list')
        self.request_data['the_geom'] = {'type':'Polygon','coordinates':[[[0,0],[0,1],[1,1],[1,0],[0,0]]]}
        response = self.client.post(url, self.request_data,format='json')
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(response.data['the_geom'],['Geometry too large: 12391399902.1 km'])

    def test_export_format_not_list_or_empty(self):
        url = reverse('api:jobs-list')
        del self.request_data['export_formats']
        response = self.client.post(url, self.request_data,format='json')
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(['This field is required.'], response.data['export_formats'])

        self.request_data['export_formats'] = {'shp':True}
        response = self.client.post(url, self.request_data,format='json')
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertTrue('export_formats' in response.data)

class TestConfigurationViewSet(APITestCase):
    def setUp(self, ):
        self.user = User.objects.create(username='demo', email='demo@demo.com', password='demo')
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key,
                                HTTP_ACCEPT='application/json; version=1.0',
                                HTTP_ACCEPT_LANGUAGE='en',
                                HTTP_HOST='testserver')
        self.request_data = {
            'name':'My Configuration',
            'description':'Configuration for Health and Sanitation',
            'yaml':FeatureSelection.example_raw("simple") ,
            'public':True
        }

    def test_create_configuration(self):
        url = reverse('api:configurations-list')
        response = self.client.post(url,self.request_data, format="json")
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"]["username"],"demo")

    def test_invalid_configuration(self):
        self.request_data["yaml"] = " - foo"
        url = reverse('api:configurations-list')
        response = self.client.post(url,self.request_data, format="json")
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEquals(response.data['yaml'],[u"YAML must be dict, not list"])


class TestExportRunViewSet(APITestCase):
    """
    Test cases for ExportRunViewSet
    """

    def setUp(self, ):
        self.user = User.objects.create(username='demo', email='demo@demo.com', password='demo')
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key,
                                HTTP_ACCEPT='application/json; version=1.0',
                                HTTP_ACCEPT_LANGUAGE='en',
                                HTTP_HOST='testserver')

        the_geom = Polygon.from_bbox((-10.80029,6.3254236,-10.79809,6.32752))
        self.job = Job.objects.create(
            name='TestJob',
            user=self.user,
            the_geom=the_geom,
            export_formats=['shp'],
            feature_selection=FeatureSelection.example('simple')
        )
        run = ExportRun.objects.create(
            job=self.job,
            user=self.user
        )
        ExportTask.objects.create(
            run=run
        )


    def test_list_runs(self):
        url = reverse('api:runs-list')
        query = '{0}?job_uid={1}'.format(url, self.job.uid)
        response = self.client.get(query)
        result = response.data
        self.assertEquals(1, len(result))
        self.assertEquals(1, len(result[0]['tasks']))

    @patch('api.views.ExportTaskRunner')
    def test_create_run(self, mock):
        url = reverse('api:runs-list')
        query = '{0}?job_uid={1}'.format(url, self.job.uid)
        response = self.client.post(query)
        task_runner = mock.return_value
        task_runner.run_task.assert_called_once_with(job_uid=str(self.job.uid),user=self.user)

class TestHDXExportRegionViewSet(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='demo', email='demo@demo.com', password='demo',is_superuser=True
        )
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key,
                                HTTP_ACCEPT='application/json; version=1.0',
                                HTTP_ACCEPT_LANGUAGE='en',
                                HTTP_HOST='testserver')
        self.request_data = {
            'name': 'TestHDXRegion',
            'export_formats': ["shp"],
            'the_geom':{'type':'Polygon','coordinates':[[[-17.464,14.727],[-17.449,14.727],[-17.449,14.740],[-17.464,14.740],[-17.464,14.727]]]},
            'feature_selection':FeatureSelection.example_raw("simple"),
            'dataset_prefix':'hdx_test_',
            'locations':['SEN'],
            'is_private':True,
            'buffer_aoi':True,
            'schedule_period':'daily',
            'schedule_hour':0,
            'subnational':True,
            'extra_notes':'',
            'license':''
        }

    def test_create_region_success(self):
        url = reverse("api:hdx_export_regions-list")
        response = self.client.post(url, self.request_data,format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        j = Job.objects.get(uid=response.data['job_uid'])
        self.assertTrue(j.hidden)
        self.assertTrue(j.unlimited_extent)

    def test_create_region_permission(self):
        self.user = User.objects.create_user(
            username='anon', email='anon@anon.com', password='anon',is_superuser=False
        )
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key,
                                HTTP_ACCEPT='application/json; version=1.0',
                                HTTP_ACCEPT_LANGUAGE='en',
                                HTTP_HOST='testserver')
        url = reverse("api:hdx_export_regions-list")
        response = self.client.post(url, self.request_data,format='json')
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_region_validates_job_attributes(self):
        self.request_data['feature_selection'] = '- invalid yaml'
        url = reverse("api:hdx_export_regions-list")
        response = self.client.post(url, self.request_data,format='json')
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(response.data['feature_selection'],[u"YAML must be dict, not list"])

    def test_create_region_validates_region_attributes(self):
        self.request_data['dataset_prefix'] = "InvalidPrefixWithCaps"
        url = reverse("api:hdx_export_regions-list")
        response = self.client.post(url, self.request_data,format='json')
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertTrue("dataset_prefix" in response.data)

    def test_update_region_success(self):
        url = reverse("api:hdx_export_regions-list")
        response = self.client.post(url, self.request_data,format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        url = reverse("api:hdx_export_regions-detail",args=[response.data['id']])
        self.request_data['name'] = 'NewRegionName'
        self.request_data['dataset_prefix'] = 'new_prefix'
        response = self.client.put(url, self.request_data,format='json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['name'],'NewRegionName')
        self.assertEquals(response.data['dataset_prefix'],'new_prefix')

    def test_update_region_validates_job_attributes(self):
        url = reverse("api:hdx_export_regions-list")
        response = self.client.post(url, self.request_data,format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        url = reverse("api:hdx_export_regions-detail",args=[response.data['id']])
        self.request_data['feature_selection'] = '- invalid yaml'
        response = self.client.put(url, self.request_data,format='json')
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(response.data['feature_selection'],[u"YAML must be dict, not list"])

    def test_update_region_validates_region_attributes(self):
        url = reverse("api:hdx_export_regions-list")
        response = self.client.post(url, self.request_data,format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        url = reverse("api:hdx_export_regions-detail",args=[response.data['id']])
        self.request_data['dataset_prefix'] = 'InvalidPrefixWithCaps'
        response = self.client.put(url, self.request_data,format='json')
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertTrue("dataset_prefix" in response.data)


class TestBBoxSearch(APITestCase):
    """
    Test cases for testing bounding box searches.
    """
    @patch('api.views.ExportTaskRunner')
    @skip('')
    def setUp(self, mock):
        task_runner = mock.return_value
        url = reverse('api:jobs-list')
        # create dummy user
        Group.objects.create(name='TestDefaultExportExtentGroup')
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



