import logging
import json
import uuid
import os
from django.test import TestCase
from django.core.files import File
from unittest import skip
from rest_framework.reverse import reverse
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry, Polygon
from rest_framework.test import APITestCase, APITransactionTestCase
from rest_framework.authtoken.models import Token
from mock import Mock, PropertyMock, patch
from tasks.task_runners import ExportTaskRunner
from jobs.models import Job, ExportFormat, ExportConfig
from tasks.models import ExportTask
from api.pagination import JobLinkHeaderPagination
from api.views import ExportConfigViewSet

logger = logging.getLogger(__name__)


class TestJobViewSet(APITestCase):
    
    def setUp(self, ):
        self.user = User.objects.create_user(
            username='demo', email='demo@demo.com', password='demo'
        )
        extents = (-3.9, 16.1, 7.0, 27.6)
        bbox = Polygon.from_bbox(extents)
        the_geom = GEOSGeometry(bbox, srid=4326)
        self.job = Job.objects.create(name='TestJob',
                                 description='Test description', user=self.user,
                                 the_geom=the_geom)
        format = ExportFormat.objects.get(slug='obf')
        self.job.formats.add(format)
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
                "exports":[{"uid":"8611792d-3d99-4c8f-a213-787bc7f3066",
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
        self.assertEqual(response.data['exports'][0]['url'], data['exports'][0]['url'])
    
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
        formats = [format.slug for format in ExportFormat.objects.all()]
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
        self.assertEquals(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        
        # test significant response content
        self.assertEqual(response.data['exports'][0]['slug'], request_data['formats'][0])
        self.assertEqual(response.data['exports'][1]['slug'], request_data['formats'][1])
        self.assertEqual(response.data['name'], request_data['name'])
        self.assertEqual(response.data['description'], request_data['description'])
        #self.assertEqual(response.data['status'], 'PENDING')
    
    
    def test_missing_bbox_param(self, ):
        url = reverse('api:jobs-list')
        formats = [format.slug for format in ExportFormat.objects.all()]
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
        self.assertEquals(['xmin is required.'], response.data['xmin'])
        
    def test_invalid_bbox_param(self, ):
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
        self.assertEquals(['invalid xmin value.'], response.data['xmin'])
    
    def test_invalid_bbox(self, ):
        url = reverse('api:jobs-list')
        formats = [format.slug  for format in ExportFormat.objects.all()]
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
        self.assertEquals(['invalid_bounds'], response.data['id'])
    
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
        self.assertEquals(["Ensure this value is greater than or equal to -180."], response.data['xmin'])
        
    def test_coord_nan(self, ):
        url = reverse('api:jobs-list')
        formats = [format.slug for format in ExportFormat.objects.all()]
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
        self.assertEquals(['invalid xmin value.'], response.data['xmin'])
        
    def test_inverted_coords(self, ):
        url = reverse('api:jobs-list')
        formats = [format.slug  for format in ExportFormat.objects.all()]
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
        self.assertEquals(['inverted_coordinates'], response.data['id'])
    
    def test_empty_string_param(self, ):
        url = reverse('api:jobs-list')
        formats = [format.slug  for format in ExportFormat.objects.all()]
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
        self.assertEquals(['This field may not be blank.'], response.data['description'])
        
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
        self.assertEquals(['Select an export format.'], response.data['formats'])
    
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
        self.assertIsNotNone(response.data['formats'])
        
    def test_no_matching_format_slug(self, ):
        url = reverse('api:jobs-list')
        request_data = {
            'name': 'TestJob',
            'description': 'Test description',
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
        formats = [format.slug  for format in ExportFormat.objects.all()]
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
        formats = [format.slug  for format in ExportFormat.objects.all()]
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
        self.assertEquals(['invalid_region'], response.data['id'])
    
    def test_extents_too_large(self, ):
        url = reverse('api:jobs-list')
        formats = [format.slug for format in ExportFormat.objects.all()]
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
        extents = [(-3.9, 16.1, 7.0, 27.6),(36.90, 13.54, 48.52, 20.24),
            (-71.79, -49.57, -67.14, -46.16), (-61.27, -6.49, -56.20, -2.25),
            (-11.61, 32.07, -6.42, 36.31), (-10.66, 5.81, -2.45, 11.83),
            (47.26, 34.58, 52.92, 39.15), (90.00, 11.28, 95.74, 17.02)]
        for extent in extents:
            request_data = {
                'name': 'TestJob',
                'description': 'Test description',
                'xmin': extent[0],
                'ymin': extent[1],
                'xmax': extent[2],
                'ymax': extent[3],
                'formats': formats
            }
            response = self.client.post(url, request_data)
            self.assertEquals(status.HTTP_202_ACCEPTED, response.status_code)
        self.assertEquals(8, len(Job.objects.all()))
        JobLinkHeaderPagination.page_size = 2
        
    def test_bbox_search_success(self, ):
        url = reverse('api:jobs-list')
        extent = (-79.5, -16.16, 7.40, 52.44)
        param = 'bbox={0},{1},{2},{3}'.format(extent[0], extent[1], extent[2], extent[3])
        response = self.client.get('{0}?{1}'.format(url, param))
        self.assertEquals(2, len(response.data)) # 8 jobs in total but response is paginated
        
    def test_list_jobs_no_bbox(self, ):
        url = reverse('api:jobs-list')
        response = self.client.get(url)
        self.assertEquals(status.HTTP_206_PARTIAL_CONTENT, response.status_code)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        self.assertEquals(response['Link'], '<http://testserver/api/jobs?page=2; rel="next">')
        self.assertEquals(2, len(response.data)) # 8 jobs in total but response is paginated
    

    def test_bbox_search_missing_params(self, ):
        url = reverse('api:jobs-list')
        param = 'bbox=' # missing params
        response = self.client.get('{0}?{1}'.format(url, param))
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        self.assertEquals('missing_bbox_parameter', response.data['id'])
    
    def test_bbox_missing_coord(self, ):
        url = reverse('api:jobs-list')
        extent = (-79.5, -16.16, 7.40) # one missing 
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
    @patch('tasks.export_tasks.ShpExportTask')
    def setUp(self, mock):
        user = User.objects.create(username='demo', email='demo@demo.com', password='demo')
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key,
                                HTTP_ACCEPT='application/json; version=1.0',
                                HTTP_ACCEPT_LANGUAGE='en',
                                HTTP_HOST='testserver')
        export_task = mock.return_value
        celery_uid = str(uuid.uuid4())
        export_task.delay.return_value = Mock(state='PENDING', id=celery_uid)
        type(export_task).name = PropertyMock(return_value='Shapefile Export')
        url = reverse('api:jobs-list')
        formats = [format.slug for format in ExportFormat.objects.filter(slug='shp')]
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
        self.job_uid = response.data['uid']
        
        # test the response headers
        self.assertEquals(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        
        # test significant response content
        self.assertEqual(response.data['exports'][0]['slug'], request_data['formats'][0])
        self.assertEqual(response.data['name'], request_data['name'])
        self.assertEqual(response.data['description'], request_data['description'])
        
        export_task.delay.assert_called_once_with(job_uid=self.job_uid)
        export_task.delay.return_value.assert_called('state')
        export_task.delay.return_value.assert_called('id')
        
    def test_list_runs(self, ):
        expected = '/api/runs/{0}'.format(self.job_uid)
        url = reverse('api:runs-detail', args=[self.job_uid])
        self.assertEquals(expected, url)
        response = self.client.get(url)
        self.assertIsNotNone(response)
        

class TestExportConfigViewSet(APITestCase):
    
    def setUp(self, ):
        self.path = os.path.dirname(os.path.realpath(__file__))
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
        response = self.client.post(url, {'upload': f, 'config_type': 'TRANSFORM'}, format='multipart')
        data = response.data
        uid = data['uid']
        saved_config = ExportConfig.objects.get(uid=uid)
        self.assertIsNotNone(saved_config)
        self.assertEquals('example_transform.sql', saved_config.filename)
        self.assertEquals('text/plain', saved_config.content_type)
        saved_config.delete()
        
    def test_invalid_config_type(self, ):
        url = reverse('api:configs-list')
        path = os.path.dirname(os.path.realpath(__file__))
        f = open(path + '/files/Example Transform.sql', 'r')
        self.assertIsNotNone(f)
        response = self.client.post(url, {'upload': f, 'config_type': 'TRANSFORM-WRONG'}, format='multipart')
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        
    def test_invalid_upload(self, ):
        url = reverse('api:configs-list')
        response = self.client.post(url, {'upload': '', 'config_type': 'TRANSFORM-WRONG'}, format='multipart')
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        
    def test_update_config(self, ):
        url = reverse('api:configs-list')
        # create an initial config we can then update..
        path = os.path.dirname(os.path.realpath(__file__))
        f = File(open(path + '/files/Example Transform.sql', 'r'))
        response = self.client.post(url, {'upload': f, 'config_type': 'TRANSFORM'}, format='multipart')
        data = response.data
        saved_uid = data['uid']
        saved_config = ExportConfig.objects.get(uid=saved_uid)
        
        # update the config
        url = reverse('api:configs-detail', args=[saved_uid])
        f = File(open(path + '/files/boundary_preset.xml', 'r'))
        response = self.client.put(url, {'upload': f, 'config_type': 'PRESET'}, format='multipart')
        data = response.data
        updated_uid = data['uid']
        self.assertEquals(saved_uid, updated_uid) # check its the same uid
        updated_config = ExportConfig.objects.get(uid=updated_uid)
        self.assertIsNotNone(updated_config)
        self.assertEquals('boundary_preset.xml', updated_config.filename)
        self.assertEquals('application/xml', updated_config.content_type)
        updated_config.delete()
        try:
            f = File(open(path + '/files/Example Transform.sql', 'r'))
        except IOError:
            pass #expected.. old file has been deleted during update.
        
        
