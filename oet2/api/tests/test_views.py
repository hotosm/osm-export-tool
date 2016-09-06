# -*- coding: utf-8 -*-
import json
import logging
import os
import uuid
from unittest import skip

from mock import patch

from django.contrib.auth.models import Group, User
from django.contrib.gis.geos import GEOSGeometry, Polygon
from django.core.files import File

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from oet2.api.pagination import LinkHeaderPagination
from oet2.jobs.models import ExportConfig, ExportFormat, ExportProfile, Job
from oet2.tasks.models import ExportRun, ExportTask

logger = logging.getLogger(__name__)


class TestJobViewSet(APITestCase):

    def setUp(self, ):
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.group = Group.objects.create(name='TestDefaultExportExtentGroup')
        profile = ExportProfile.objects.create(
            name='DefaultExportProfile',
            max_extent=2500000,
            group=self.group
        )
        self.user = User.objects.create_user(
            username='demo', email='demo@demo.com', password='demo'
        )
        extents = (-3.9, 16.1, 7.0, 27.6)
        bbox = Polygon.from_bbox(extents)
        the_geom = GEOSGeometry(bbox, srid=4326)
        self.job = Job.objects.create(name='TestJob', event='Test Activation',
                                 description='Test description', user=self.user,
                                 the_geom=the_geom)
        format = ExportFormat.objects.get(slug='obf')
        self.job.formats.add(format)
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key,
                                HTTP_ACCEPT='application/json; version=1.0',
                                HTTP_ACCEPT_LANGUAGE='en',
                                HTTP_HOST='testserver')
        # create a test config
        f = File(open(self.path + '/files/hdm_presets.xml'))
        filename = f.name.split('/')[-1]
        name = 'Test Configuration File'
        self.config = ExportConfig.objects.create(name='Test Preset Config', filename=filename, upload=f, config_type='PRESET', user=self.user)
        f.close()
        self.assertIsNotNone(self.config)
        self.job.configs.add(self.config)
        self.tags = [
                {
                    "name": "Telecommunication office",
                    "key": "office", "value": "telecommunication",
                    "data_model": "HDM",
                    "geom_types": ["point", "polygon"],
                    "groups": ['HDM Presets v2.11', 'Commercial and Economic', 'Telecommunication']
                },
                {
                    "name": "Radio or TV Studio",
                    "key": "amenity", "value": "studio",
                    "data_model": "OSM",
                    "geom_types": ["point", "polygon"],
                    "groups": ['HDM Presets v2.11', 'Commercial and Economic', 'Telecommunication']
                },
                {
                    "name": "Telecommunication antenna",
                    "key": "man_made", "value": "tower",
                    "data_model": "OSM",
                    "geom_types": ["point", "polygon"],
                    "groups": ['HDM Presets v2.11', 'Commercial and Economic', 'Telecommunication']
                },
                {
                    "name": "Telecommunication company retail office",
                    "key": "office", "value": "telecommunication",
                    "data_model": "OSM",
                    "geom_types": ["point", "polygon"],
                    "groups": ['HDM Presets v2.11', 'Commercial and Economic', 'Telecommunication']
                }
            ]

    def tearDown(self,):
        self.config.delete()  # clean up

    def test_list(self, ):
        expected = '/api/jobs'
        url = reverse('api:jobs-list')
        self.assertEquals(expected, url)

    def test_get_job_detail(self, ):
        expected = '/api/jobs/{0}'.format(self.job.uid)
        url = reverse('api:jobs-detail', args=[self.job.uid])
        self.assertEquals(expected, url)
        data = {"uid": str(self.job.uid),
                "name": "Test",
                "url": 'http://testserver{0}'.format(url),
                "description": "Test Description",
                "exports": [{"uid": "8611792d-3d99-4c8f-a213-787bc7f3066",
                            "url": "http://testserver/api/formats/obf",
                            "name": "OBF Format",
                            "description": "OSMAnd OBF Export Format."}],
                "created_at": "2015-05-21T19:46:37.163749Z",
                "updated_at": "2015-05-21T19:46:47.207111Z",
                "status": "SUCCESS"}
        response = self.client.get(url)
        # test the response headers
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')

        # test significant content
        self.assertEquals(response.data['uid'], data['uid'])
        self.assertEquals(response.data['url'], data['url'])
        self.assertEqual(response.data['exports'][0]['url'], data['exports'][0]['url'])

    def test_delete_job(self, ):
        url = reverse('api:jobs-detail', args=[self.job.uid])
        response = self.client.delete(url)
        # test the response headers
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEquals(response['Content-Length'], '0')
        self.assertEquals(response['Content-Language'], 'en')

    def test_delete_no_permissions(self, ):
        url = reverse('api:jobs-detail', args=[self.job.uid])
        # create another user with token
        user = User.objects.create_user(
            username='other_user', email='other_user@demo.com', password='demo'
        )
        token = Token.objects.create(user=user)
        # reset the client credentials to the new user
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key,
                                HTTP_ACCEPT='application/json; version=1.0',
                                HTTP_ACCEPT_LANGUAGE='en',
                                HTTP_HOST='testserver')
        # try to delete a job belonging to self.user
        response = self.client.delete(url)
        # test the response headers
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('api.views.ExportTaskRunner')
    def test_create_job_success(self, mock):
        task_runner = mock.return_value
        url = reverse('api:jobs-list')
        formats = [format.slug for format in ExportFormat.objects.all()]
        config_uid = self.config.uid
        request_data = {
            'name': 'TestJob',
            'description': 'Test description',
            'event': 'Test Activation',
            'xmin': -3.9,
            'ymin': 16.1,
            'xmax': 7.0,
            'ymax': 27.6,
            'formats': formats,
            'preset': config_uid,
            'published': True,
            'tags': self.tags
        }
        response = self.client.post(url, request_data, format='json')
        job_uid = response.data['uid']
        # test the ExportTaskRunner.run_task(job_id) method gets called.
        task_runner.run_task.assert_called_once_with(job_uid=job_uid)

        # test the response headers
        self.assertEquals(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')

        # test significant response content
        self.assertEqual(response.data['exports'][0]['slug'], request_data['formats'][0])
        self.assertEqual(response.data['exports'][1]['slug'], request_data['formats'][1])
        self.assertEqual(response.data['name'], request_data['name'])
        self.assertEqual(response.data['description'], request_data['description'])
        self.assertTrue(response.data['published'])

        # check we have the correct tags
        job = Job.objects.get(uid=job_uid)
        tags = job.tags.all()
        self.assertIsNotNone(tags)
        self.assertEquals(233, len(tags))

    @patch('api.views.ExportTaskRunner')
    def test_create_job_with_config_success(self, mock):
        task_runner = mock.return_value
        config_uid = self.config.uid
        url = reverse('api:jobs-list')
        formats = [format.slug for format in ExportFormat.objects.all()]
        request_data = {
            'name': 'TestJob',
            'description': 'Test description',
            'event': 'Test Activation',
            'xmin': -3.9,
            'ymin': 16.1,
            'xmax': 7.0,
            'ymax': 27.6,
            'formats': formats,
            'preset': config_uid,
            'transform': '',
            'translation': ''

        }
        response = self.client.post(url, request_data, format='json')
        job_uid = response.data['uid']
        # test the ExportTaskRunner.run_task(job_id) method gets called.
        task_runner.run_task.assert_called_once_with(job_uid=job_uid)

        # test the response headers
        self.assertEquals(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')

        # test significant response content
        self.assertEqual(response.data['exports'][0]['slug'], request_data['formats'][0])
        self.assertEqual(response.data['exports'][1]['slug'], request_data['formats'][1])
        self.assertEqual(response.data['name'], request_data['name'])
        self.assertEqual(response.data['description'], request_data['description'])
        self.assertFalse(response.data['published'])
        configs = self.job.configs.all()
        self.assertIsNotNone(configs[0])

    @patch('api.views.ExportTaskRunner')
    def test_create_job_with_tags(self, mock):
        # delete the existing tags and test adding them with json
        self.job.tags.all().delete()
        task_runner = mock.return_value
        config_uid = self.config.uid
        url = reverse('api:jobs-list')
        formats = [format.slug for format in ExportFormat.objects.all()]
        request_data = {
            'name': 'TestJob',
            'description': 'Test description',
            'event': 'Test Activation',
            'xmin': -3.9,
            'ymin': 16.1,
            'xmax': 7.0,
            'ymax': 27.6,
            'formats': formats,
            # 'preset': config_uid,
            'transform': '',
            'translate': '',
            'tags': self.tags
        }
        response = self.client.post(url, request_data, format='json')
        job_uid = response.data['uid']
        # test the ExportTaskRunner.run_task(job_id) method gets called.
        task_runner.run_task.assert_called_once_with(job_uid=job_uid)

        # test the response headers
        self.assertEquals(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')

        # test significant response content
        self.assertEqual(response.data['exports'][0]['slug'], request_data['formats'][0])
        self.assertEqual(response.data['exports'][1]['slug'], request_data['formats'][1])
        self.assertEqual(response.data['name'], request_data['name'])
        self.assertEqual(response.data['description'], request_data['description'])
        configs = self.job.configs.all()
        # self.assertIsNotNone(configs[0])

    def test_missing_bbox_param(self, ):
        url = reverse('api:jobs-list')
        formats = [format.slug for format in ExportFormat.objects.all()]
        request_data = {
            'name': 'TestJob',
            'description': 'Test description',
            'event': 'Test Activation',
            # 'xmin': -3.9, missing
            'ymin': 16.1,
            'xmax': 7.0,
            'ymax': 27.6,
            'formats': formats
        }
        response = self.client.post(url, request_data)
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        self.assertEquals(['xmin is required.'], response.data['xmin'])

    def test_invalid_bbox_param(self, ):
        url = reverse('api:jobs-list')
        formats = [str(format.uid) for format in ExportFormat.objects.all()]
        request_data = {
            'name': 'TestJob',
            'description': 'Test description',
            'event': 'Test Activation',
            'xmin': '',  # empty
            'ymin': 16.1,
            'xmax': 7.0,
            'ymax': 27.6,
            'formats': formats
        }
        response = self.client.post(url, request_data, format='json')
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        self.assertEquals(['invalid xmin value.'], response.data['xmin'])

    def test_invalid_bbox(self, ):
        url = reverse('api:jobs-list')
        formats = [format.slug for format in ExportFormat.objects.all()]
        request_data = {
            'name': 'TestJob',
            'description': 'Test description',
            'event': 'Test Activation',
            'xmin': 7.0,  # invalid
            'ymin': 16.1,
            'xmax': 7.0,
            'ymax': 27.6,
            'formats': formats
        }
        response = self.client.post(url, request_data)
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        self.assertEquals(['invalid_bounds'], response.data['id'])

    def test_lat_lon_bbox(self, ):
        url = reverse('api:jobs-list')
        formats = [str(format.uid) for format in ExportFormat.objects.all()]
        request_data = {
            'name': 'TestJob',
            'description': 'Test description',
            'event': 'Test Activation',
            'xmin': -227.14,  # invalid
            'ymin': 16.1,
            'xmax': 7.0,
            'ymax': 27.6,
            'formats': formats
        }
        response = self.client.post(url, request_data)
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        self.assertEquals(["Ensure this value is greater than or equal to -180."], response.data['xmin'])

    def test_coord_nan(self, ):
        url = reverse('api:jobs-list')
        formats = [format.slug for format in ExportFormat.objects.all()]
        request_data = {
            'name': 'TestJob',
            'description': 'Test description',
            'event': 'Test Activation',
            'xmin': 'xyz',  # invalid
            'ymin': 16.1,
            'xmax': 7.0,
            'ymax': 27.6,
            'formats': formats
        }
        response = self.client.post(url, request_data)
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        self.assertEquals(['invalid xmin value.'], response.data['xmin'])

    def test_inverted_coords(self, ):
        url = reverse('api:jobs-list')
        formats = [format.slug for format in ExportFormat.objects.all()]
        request_data = {
            'name': 'TestJob',
            'description': 'Test description',
            'event': 'Test Activation',
            'xmin': 7.0,  # inverted
            'ymin': 16.1,
            'xmax': -3.9,  # inverted
            'ymax': 27.6,
            'formats': formats
        }
        response = self.client.post(url, request_data)
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        self.assertEquals(['inverted_coordinates'], response.data['id'])

    def test_empty_string_param(self, ):
        url = reverse('api:jobs-list')
        formats = [format.slug for format in ExportFormat.objects.all()]
        request_data = {
            'name': 'TestJob',
            'description': '',  # empty
            'event': 'Test Activation',
            'xmin': -3.9,
            'ymin': 16.1,
            'xmax': 7.0,
            'ymax': 27.6,
            'formats': formats
        }
        response = self.client.post(url, request_data)
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        self.assertEquals(['This field may not be blank.'], response.data['description'])

    def test_missing_format_param(self, ):
        url = reverse('api:jobs-list')
        request_data = {
            'name': 'TestJob',
            'description': 'Test description',
            'event': 'Test Activation',
            'xmin': -3.9,
            'ymin': 16.1,
            'xmax': 7.0,
            'ymax': 27.6,
            # 'formats': '', # missing
        }
        response = self.client.post(url, request_data)
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        self.assertEquals(['Select an export format.'], response.data['formats'])

    def test_invalid_format_param(self, ):
        url = reverse('api:jobs-list')
        request_data = {
            'name': 'TestJob',
            'description': 'Test description',
            'event': 'Test Activation',
            'xmin': -3.9,
            'ymin': 16.1,
            'xmax': 7.0,
            'ymax': 27.6,
            'formats': '',  # invalid
        }
        response = self.client.post(url, request_data)
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        self.assertIsNotNone(response.data['formats'])

    def test_no_matching_format_slug(self, ):
        url = reverse('api:jobs-list')
        request_data = {
            'name': 'TestJob',
            'description': 'Test description',
            'event': 'Test Activation',
            'xmin': -3.9,
            'ymin': 16.1,
            'xmax': 7.0,
            'ymax': 27.6,
            'formats': ['broken-format-one', 'broken-format-two']
        }
        response = self.client.post(url, request_data)
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        self.assertEquals(response.data['formats'], ['invalid export format.'])

    @patch('api.views.ExportTaskRunner')
    def test_get_correct_region(self, mock):
        task_runner = mock.return_value
        url = reverse('api:jobs-list')
        formats = [format.slug for format in ExportFormat.objects.all()]
        # job extent spans africa / asia but greater intersection with asia
        request_data = {
            'name': 'TestJob',
            'description': 'Test description',
            'event': 'Test Activation',
            'xmin': 36.90,
            'ymin': 13.54,
            'xmax': 48.52,
            'ymax': 20.24,
            'formats': formats
        }
        response = self.client.post(url, request_data, format='json')
        job_uid = response.data['uid']
        # test the ExportTaskRunner.run_task(job_id) method gets called.
        task_runner.run_task.assert_called_once_with(job_uid=job_uid)

        # test the response headers
        self.assertEquals(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')

        # test significant response content
        self.assertEqual(response.data['exports'][0]['slug'], request_data['formats'][0])
        self.assertEqual(response.data['exports'][1]['slug'], request_data['formats'][1])
        self.assertEqual(response.data['name'], request_data['name'])
        self.assertEqual(response.data['description'], request_data['description'])

        # test the region
        region = response.data['region']
        self.assertIsNotNone(region)
        self.assertEquals(region['name'], 'Central Asia/Middle East')

    def test_invalid_region(self, ):
        url = reverse('api:jobs-list')
        formats = [format.slug for format in ExportFormat.objects.all()]
        # job outside any region
        request_data = {
            'name': 'TestJob',
            'description': 'Test description',
            'event': 'Test Activation',
            'xmin': 2.74,
            'ymin': 47.66,
            'xmax': 11.61,
            'ymax': 54.24,
            'formats': formats
        }
        response = self.client.post(url, request_data)
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        self.assertEquals(['invalid_region'], response.data['id'])

    def test_extents_too_large(self, ):
        url = reverse('api:jobs-list')
        formats = [format.slug for format in ExportFormat.objects.all()]
        # job outside any region
        request_data = {
            'name': 'TestJob',
            'description': 'Test description',
            'event': 'Test Activation',
            'xmin': -40,
            'ymin': -10,
            'xmax': 40,
            'ymax': 20,
            'formats': formats
        }
        response = self.client.post(url, request_data)
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        self.assertEquals(['invalid_extents'], response.data['id'])


class TestBBoxSearch(APITestCase):
    """
    Test cases for testing bounding box searches.
    """
    @patch('api.views.ExportTaskRunner')
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
        formats = [format.slug for format in ExportFormat.objects.all()]
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
                'formats': formats
            }
            response = self.client.post(url, request_data, format='json')
            self.assertEquals(status.HTTP_202_ACCEPTED, response.status_code)
        self.assertEquals(8, len(Job.objects.all()))
        LinkHeaderPagination.page_size = 2

    def test_bbox_search_success(self, ):
        url = reverse('api:jobs-list')
        extent = (-79.5, -16.16, 7.40, 52.44)
        param = 'bbox={0},{1},{2},{3}'.format(extent[0], extent[1], extent[2], extent[3])
        response = self.client.get('{0}?{1}'.format(url, param))
        self.assertEquals(status.HTTP_206_PARTIAL_CONTENT, response.status_code)
        self.assertEquals(2, len(response.data))  # 8 jobs in total but response is paginated

    def test_list_jobs_no_bbox(self, ):
        url = reverse('api:jobs-list')
        response = self.client.get(url)
        self.assertEquals(status.HTTP_206_PARTIAL_CONTENT, response.status_code)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        self.assertEquals(response['Link'], '<http://testserver/api/jobs?page=2>; rel="next"')
        self.assertEquals(2, len(response.data))  # 8 jobs in total but response is paginated

    def test_bbox_search_missing_params(self, ):
        url = reverse('api:jobs-list')
        param = 'bbox='  # missing params
        response = self.client.get('{0}?{1}'.format(url, param))
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        self.assertEquals('missing_bbox_parameter', response.data['id'])

    def test_bbox_missing_coord(self, ):
        url = reverse('api:jobs-list')
        extent = (-79.5, -16.16, 7.40)  # one missing
        param = 'bbox={0},{1},{2}'.format(extent[0], extent[1], extent[2])
        response = self.client.get('{0}?{1}'.format(url, param))
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        self.assertEquals('missing_bbox_parameter', response.data['id'])


class TestPagination(APITestCase):
    pass


class TestExportRunViewSet(APITestCase):
    """
    Test cases for ExportRunViewSet
    """

    def setUp(self, ):
        Group.objects.create(name='TestDefaultExportExtentGroup')
        self.user = User.objects.create(username='demo', email='demo@demo.com', password='demo')
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key,
                                HTTP_ACCEPT='application/json; version=1.0',
                                HTTP_ACCEPT_LANGUAGE='en',
                                HTTP_HOST='testserver')
        extents = (-3.9, 16.1, 7.0, 27.6)
        bbox = Polygon.from_bbox(extents)
        the_geom = GEOSGeometry(bbox, srid=4326)
        self.job = Job.objects.create(name='TestJob',
                                 description='Test description', user=self.user,
                                 the_geom=the_geom)
        self.job_uid = str(self.job.uid)
        self.run = ExportRun.objects.create(job=self.job, user=self.user)
        self.run_uid = str(self.run.uid)

    def test_retrieve_run(self, ):
        expected = '/api/runs/{0}'.format(self.run_uid)
        url = reverse('api:runs-detail', args=[self.run_uid])
        self.assertEquals(expected, url)
        response = self.client.get(url)
        self.assertIsNotNone(response)
        result = response.data
        # make sure we get the correct uid back out
        self.assertEquals(self.run_uid, result[0].get('uid'))

    def test_list_runs(self, ):
        expected = '/api/runs'
        url = reverse('api:runs-list')
        self.assertEquals(expected, url)
        query = '{0}?job_uid={1}'.format(url, self.job.uid)
        response = self.client.get(query)
        self.assertIsNotNone(response)
        result = response.data
        # make sure we get the correct uid back out
        self.assertEquals(1, len(result))
        self.assertEquals(self.run_uid, result[0].get('uid'))


class TestExportConfigViewSet(APITestCase):
    """
    Test cases for ExportConfigViewSet
    """

    def setUp(self, ):
        self.path = os.path.dirname(os.path.realpath(__file__))
        Group.objects.create(name='TestDefaultExportExtentGroup')
        self.user = User.objects.create(username='demo', email='demo@demo.com', password='demo')
        bbox = Polygon.from_bbox((-7.96, 22.6, -8.14, 27.12))
        the_geom = GEOSGeometry(bbox, srid=4326)
        self.job = Job.objects.create(name='TestJob',
                                 description='Test description', user=self.user,
                                 the_geom=the_geom)
        self.uid = self.job.uid
        # setup token authentication
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key,
                                HTTP_ACCEPT='application/json; version=1.0',
                                HTTP_ACCEPT_LANGUAGE='en',
                                HTTP_HOST='testserver')

    def test_create_config(self, ):
        url = reverse('api:configs-list')
        path = os.path.dirname(os.path.realpath(__file__))
        f = File(open(path + '/files/Example Transform.sql', 'r'))
        name = 'Test Export Config'
        response = self.client.post(url, {'name': name, 'upload': f, 'config_type': 'TRANSFORM', 'published': True}, format='multipart')
        data = response.data
        uid = data['uid']
        saved_config = ExportConfig.objects.get(uid=uid)
        self.assertIsNotNone(saved_config)
        self.assertEquals(name, saved_config.name)
        self.assertTrue(saved_config.published)
        self.assertEquals('example_transform.sql', saved_config.filename)
        self.assertEquals('text/plain', saved_config.content_type)
        saved_config.delete()

    def test_delete_no_permissions(self, ):
        """
        Test deletion of configuration when the user has no object permissions.
        """
        post_url = reverse('api:configs-list')
        path = os.path.dirname(os.path.realpath(__file__))
        f = File(open(path + '/files/hdm_presets.xml', 'r'))
        name = 'Test Export Preset'
        response = self.client.post(post_url, {'name': name, 'upload': f, 'config_type': 'PRESET', 'published': True}, format='multipart')
        data = response.data
        uid = data['uid']
        saved_config = ExportConfig.objects.get(uid=uid)
        self.assertIsNotNone(saved_config)
        self.assertEquals(name, saved_config.name)
        self.assertTrue(saved_config.published)
        self.assertEquals('hdm_presets.xml', saved_config.filename)
        self.assertEquals('application/xml', saved_config.content_type)

        delete_url = reverse('api:configs-detail', args=[uid])
        # create another user with token
        user = User.objects.create_user(
            username='other_user', email='other_user@demo.com', password='demo'
        )
        token = Token.objects.create(user=user)
        # reset the client credentials to the new user
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key,
                                HTTP_ACCEPT='application/json; version=1.0',
                                HTTP_ACCEPT_LANGUAGE='en',
                                HTTP_HOST='testserver')
        # try to delete a configuration belonging to self.user
        response = self.client.delete(delete_url)
        # test the response headers
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)
        saved_config.delete()

    def test_invalid_config_type(self, ):
        url = reverse('api:configs-list')
        path = os.path.dirname(os.path.realpath(__file__))
        f = open(path + '/files/Example Transform.sql', 'r')
        self.assertIsNotNone(f)
        response = self.client.post(url, {'upload': f, 'config_type': 'TRANSFORM-WRONG'}, format='multipart')
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_invalid_preset(self, ):
        url = reverse('api:configs-list')
        path = os.path.dirname(os.path.realpath(__file__))
        f = open(path + '/files/invalid_hdm_presets.xml', 'r')
        self.assertIsNotNone(f)
        response = self.client.post(url, {'name': 'Invalid Preset', 'upload': f, 'config_type': 'PRESET'}, format='multipart')
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_invalid_name(self, ):
        url = reverse('api:configs-list')
        path = os.path.dirname(os.path.realpath(__file__))
        f = open(path + '/files/Example Transform.sql', 'r')
        self.assertIsNotNone(f)
        response = self.client.post(url, {'upload': f, 'config_type': 'TRANSFORM'}, format='multipart')
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(response.data['name'], ['This field is required.'])

    def test_invalid_upload(self, ):
        url = reverse('api:configs-list')
        response = self.client.post(url, {'upload': '', 'config_type': 'TRANSFORM-WRONG'}, format='multipart')
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)

    @skip('Transform not implemented.')
    def test_update_config(self, ):
        url = reverse('api:configs-list')
        # create an initial config we can then update..
        path = os.path.dirname(os.path.realpath(__file__))
        f = File(open(path + '/files/Example Transform.sql', 'r'))
        name = 'Test Export Config'
        response = self.client.post(url, {'name': name, 'upload': f, 'config_type': 'TRANSFORM'}, format='multipart')
        data = response.data
        saved_uid = data['uid']
        saved_config = ExportConfig.objects.get(uid=saved_uid)

        # update the config
        url = reverse('api:configs-detail', args=[saved_uid])
        f = File(open(path + '/files/hdm_presets.xml', 'r'))
        updated_name = 'Test Export Config Updated'
        response = self.client.put(url, {'name': updated_name, 'upload': f, 'config_type': 'PRESET'}, format='multipart')
        data = response.data
        updated_uid = data['uid']
        self.assertEquals(saved_uid, updated_uid)  # check its the same uid
        updated_config = ExportConfig.objects.get(uid=updated_uid)
        self.assertIsNotNone(updated_config)
        self.assertEquals('hdm_presets.xml', updated_config.filename)
        self.assertEquals('application/xml', updated_config.content_type)
        self.assertEquals('Test Export Config Updated', updated_config.name)
        updated_config.delete()
        try:
            f = File(open(path + '/files/Example Transform.sql', 'r'))
        except IOError:
            pass  # expected.. old file has been deleted during update.


class TestExportTaskViewSet(APITestCase):
    """
    Test cases for ExportTaskViewSet
    """

    def setUp(self, ):
        self.path = os.path.dirname(os.path.realpath(__file__))
        Group.objects.create(name='TestDefaultExportExtentGroup')
        self.user = User.objects.create(username='demo', email='demo@demo.com', password='demo')
        bbox = Polygon.from_bbox((-7.96, 22.6, -8.14, 27.12))
        the_geom = GEOSGeometry(bbox, srid=4326)
        self.job = Job.objects.create(name='TestJob',
                                 description='Test description', user=self.user,
                                 the_geom=the_geom)
        # setup token authentication
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key,
                                HTTP_ACCEPT='application/json; version=1.0',
                                HTTP_ACCEPT_LANGUAGE='en',
                                HTTP_HOST='testserver')
        self.run = ExportRun.objects.create(job=self.job)
        self.celery_uid = str(uuid.uuid4())
        self.task = ExportTask.objects.create(run=self.run, name='Shapefile Export',
                                              celery_uid=self.celery_uid, status='SUCCESS')
        self.task_uid = str(self.task.uid)

    def test_retrieve(self, ):
        expected = '/api/tasks/{0}'.format(self.task_uid)
        url = reverse('api:tasks-detail', args=[self.task_uid])
        self.assertEquals(expected, url)
        response = self.client.get(url)
        self.assertIsNotNone(response)
        self.assertEquals(200, response.status_code)
        result = json.dumps(response.data)
        data = json.loads(result)
        # make sure we get the correct uid back out
        self.assertEquals(self.task_uid, data[0].get('uid'))

    def test_list(self, ):
        expected = '/api/tasks'.format(self.task_uid)
        url = reverse('api:tasks-list')
        self.assertEquals(expected, url)
        response = self.client.get(url)
        self.assertIsNotNone(response)
        self.assertEquals(200, response.status_code)
        result = json.dumps(response.data)
        data = json.loads(result)
        # should only be one task in the list
        self.assertEquals(1, len(data))
        # make sure we get the correct uid back out
        self.assertEquals(self.task_uid, data[0].get('uid'))
