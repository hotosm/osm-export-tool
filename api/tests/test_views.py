import logging
import json
from django.test import TestCase
from unittest import skip
from rest_framework.reverse import reverse
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry, Polygon
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from mock import Mock, patch
from tasks.export_tasks import ExportTaskRunner
from jobs.models import Job, ExportFormat, ExportTask

logger = logging.getLogger(__name__)

class TestJobViewSet(APITestCase):
    
    def setUp(self, ):
        self.user = User.objects.create_user(
            username='demo', email='demo@demo.com', password='demo'
        )
        extents = (-3.9, 16.1, 7.0, 27.6)
        bbox = Polygon.from_bbox(extents)
        the_geom = GEOSGeometry(bbox, srid=4326)
        the_geog = GEOSGeometry(bbox)
        the_geom_webmercator = the_geom.transform(ct=3857, clone=True)
        self.job = Job.objects.create(name='TestJob',
                                 description='Test description', user=self.user,
                                 the_geom=the_geom, the_geog=the_geog,
                                 the_geom_webmercator=the_geom_webmercator)
        format = ExportFormat.objects.get(slug='obf')
        self.job.formats.add(format)
        self.job.save()
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key,
                                HTTP_ACCEPT='application/json; version=1.0',
                                HTTP_ACCEPT_LANGUAGE='en',
                                HTTP_HOST='testserver')
        
        
    def test_get_job_detail(self, ):
        expected = '/api/jobs/{0}'.format(self.job.uid)
        url = reverse('api:jobs-detail', args=[self.job.uid])
        self.assertEquals(expected, url)
        data = {"uid": str(self.job.uid),
                "name":"Test",
                "url": 'http://testserver{0}'.format(url),
                "description":"Test Description",
                "formats":[{"uid":"8611792d-3d99-4c8f-a213-787bc7f3066",
                            "url":"http://testserver/api/formats/obf",
                            "name":"OBF Format",
                            "description":"OSMAnd OBF Export Format."}],
                "created_at":"2015-05-21T19:46:37.163749Z",
                "updated_at":"2015-05-21T19:46:47.207111Z",
                "status":"SUCCESS"}
        response = self.client.get(url)
        # test the response headers
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        
        # test significant content
        self.assertEquals(response.data['uid'], data['uid'])
        self.assertEquals(response.data['url'], data['url'])
        self.assertEqual(response.data['formats'][0]['url'], data['formats'][0]['url'])
    
    def test_delete_job(self, ):
        url = reverse('api:jobs-detail', args=[self.job.uid])
        response = self.client.delete(url)
        # test the response headers
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEquals(response['Content-Length'], '0')
        self.assertEquals(response['Content-Language'], 'en')
    
    @patch('api.views.ExportTaskRunner')
    def test_create_job_success(self, mock):
        task_runner = mock.return_value
        url = reverse('api:jobs-list')
        formats = [str(format.uid) for format in ExportFormat.objects.all()]
        request_data = {
            'name': 'TestJob',
            'description': 'Test description',
            'xmin': -3.9,
            'ymin': 16.1,
            'xmax': 7.0,
            'ymax': 27.6,
            'formats': formats
        }
        response = self.client.post(url, request_data)
        job_uid = response.data['uid']
        # test the ExportTaskRunner.run_task(job_id) method gets called.
        task_runner.run_task.assert_called_once_with(job_uid=job_uid)
        
        # test the response headers
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        
        # test significant response content
        self.assertEqual(response.data['formats'][0]['uid'], request_data['formats'][0])
        self.assertEqual(response.data['formats'][1]['uid'], request_data['formats'][1])
        self.assertEqual(response.data['name'], request_data['name'])
        self.assertEqual(response.data['description'], request_data['description'])
        #self.assertEqual(response.data['status'], 'PENDING')
    
    def test_missing_bbox_param(self, ):
        url = reverse('api:jobs-list')
        formats = [str(format.uid) for format in ExportFormat.objects.all()]
        request_data = {
            'name': 'TestJob',
            'description': 'Test description',
            #'xmin': -3.9, missing
            'ymin': 16.1,
            'xmax': 7.0,
            'ymax': 27.6,
            'formats': formats
        }
        response = self.client.post(url, request_data)
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        self.assertEquals('missing_parameter', response.data['id'])
        self.assertEquals('xmin', response.data['param'])
        
    def test_empty_bbox_param(self, ):
        url = reverse('api:jobs-list')
        formats = [str(format.uid) for format in ExportFormat.objects.all()]
        request_data = {
            'name': 'TestJob',
            'description': 'Test description',
            'xmin': '', # empty
            'ymin': 16.1,
            'xmax': 7.0,
            'ymax': 27.6,
            'formats': formats
        }
        response = self.client.post(url, request_data)
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        self.assertEquals('empty_bbox_parameter', response.data['id'])
    
    def test_invalid_bbox(self, ):
        url = reverse('api:jobs-list')
        formats = [str(format.uid) for format in ExportFormat.objects.all()]
        request_data = {
            'name': 'TestJob',
            'description': 'Test description',
            'xmin': 7.0, # invalid
            'ymin': 16.1,
            'xmax': 7.0,
            'ymax': 27.6,
            'formats': formats
        }
        response = self.client.post(url, request_data)
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        self.assertEquals('invalid_bounds', response.data['id'])
    
    def test_lat_lon_bbox(self, ):
        url = reverse('api:jobs-list')
        formats = [str(format.uid) for format in ExportFormat.objects.all()]
        request_data = {
            'name': 'TestJob',
            'description': 'Test description',
            'xmin': -227.14, # invalid
            'ymin': 16.1,
            'xmax': 7.0,
            'ymax': 27.6,
            'formats': formats
        }
        response = self.client.post(url, request_data)
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        self.assertEquals('invalid_longitude', response.data['id'])
        
    def test_coord_nan(self, ):
        url = reverse('api:jobs-list')
        formats = [str(format.uid) for format in ExportFormat.objects.all()]
        request_data = {
            'name': 'TestJob',
            'description': 'Test description',
            'xmin': 'xyz', # invalid
            'ymin': 16.1,
            'xmax': 7.0,
            'ymax': 27.6,
            'formats': formats
        }
        response = self.client.post(url, request_data)
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        self.assertEquals('invalid_coordinate', response.data['id'])
        
    def test_inverted_coords(self, ):
        url = reverse('api:jobs-list')
        formats = [str(format.uid) for format in ExportFormat.objects.all()]
        request_data = {
            'name': 'TestJob',
            'description': 'Test description',
            'xmin': 7.0, # inverted
            'ymin': 16.1,
            'xmax': -3.9, # inverted
            'ymax': 27.6,
            'formats': formats
        }
        response = self.client.post(url, request_data)
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        self.assertEquals('inverted_coordinates', response.data['id'])
    
    def test_empty_string_param(self, ):
        url = reverse('api:jobs-list')
        formats = [str(format.uid) for format in ExportFormat.objects.all()]
        request_data = {
            'name': 'TestJob',
            'description': '',  # empty
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
        self.assertEquals('missing_parameter', response.data['id'])
        self.assertEquals('description', response.data['param'])
        
    def test_missing_format_param(self, ):
        url = reverse('api:jobs-list')
        request_data = {
            'name': 'TestJob',
            'description': 'Test description',
            'xmin': -3.9,
            'ymin': 16.1,
            'xmax': 7.0,
            'ymax': 27.6,
            #'formats': '', # missing
        }
        response = self.client.post(url, request_data)
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        self.assertEquals('missing_format', response.data['id'])
    
    def test_invalid_format_param(self, ):
        url = reverse('api:jobs-list')
        request_data = {
            'name': 'TestJob',
            'description': 'Test description',
            'xmin': -3.9,
            'ymin': 16.1,
            'xmax': 7.0,
            'ymax': 27.6,
            'formats': '', # invalid
        }
        response = self.client.post(url, request_data)
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        self.assertEquals('invalid_format_uid', response.data['id'])
    
    @patch('api.views.ExportTaskRunner')
    def test_get_correct_region(self, mock):
        task_runner = mock.return_value
        url = reverse('api:jobs-list')
        formats = [str(format.uid) for format in ExportFormat.objects.all()]
        # job extent spans africa / asia but greater intersection with asia
        request_data = {
            'name': 'TestJob',
            'description': 'Test description',
            'xmin': 36.90,
            'ymin': 13.54,
            'xmax': 48.52,
            'ymax': 20.24,
            'formats': formats
        }
        response = self.client.post(url, request_data)
        job_uid = response.data['uid']
        # test the ExportTaskRunner.run_task(job_id) method gets called.
        task_runner.run_task.assert_called_once_with(job_uid=job_uid)
        
        # test the response headers
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        
        # test significant response content
        self.assertEqual(response.data['formats'][0]['uid'], request_data['formats'][0])
        self.assertEqual(response.data['formats'][1]['uid'], request_data['formats'][1])
        self.assertEqual(response.data['name'], request_data['name'])
        self.assertEqual(response.data['description'], request_data['description'])
        
        # test the region
        region = response.data['region']
        self.assertIsNotNone(region)
        self.assertEquals(region['name'], 'Central Asia/Middle East')
    
    def test_invalid_region(self, ):
        url = reverse('api:jobs-list')
        formats = [str(format.uid) for format in ExportFormat.objects.all()]
        # job outside any region
        request_data = {
            'name': 'TestJob',
            'description': 'Test description',
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
        self.assertEquals('invalid_region', response.data['id'])
    
    def test_extents_too_large(self, ):
        url = reverse('api:jobs-list')
        formats = [str(format.uid) for format in ExportFormat.objects.all()]
        # job outside any region
        request_data = {
            'name': 'TestJob',
            'description': 'Test description',
            'xmin': 10,
            'ymin': 10,
            'xmax': 25,
            'ymax': 25,
            'formats': formats
        }
        response = self.client.post(url, request_data)
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        self.assertEquals('invalid_extents', response.data['id'])

