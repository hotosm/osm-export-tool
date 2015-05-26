import logging
import json
from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry
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
        bbox = 'POLYGON((10 10, 10 20, 20 20, 20 10, 10 10))'
        bbox_wkt = 'POLYGON((10 10, 10 20, 20 20, 20 10, 10 10))'
        the_geom = GEOSGeometry(bbox_wkt, srid=4326)
        the_geog = GEOSGeometry(bbox_wkt)
        the_geom_webmercator = the_geom.transform(ct=3857, clone=True)
        self.job = Job.objects.create(name='TestJob',
                                 description='Test description', user=self.user,
                                 the_geom=the_geom, the_geog=the_geog,
                                 the_geom_webmercator=the_geom_webmercator)
        format = ExportFormat.objects.get(slug='obf')
        self.job.formats.add(format)
        self.job.save()
        
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
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key,
                                HTTP_ACCEPT='application/json; version=1.0',
                                HTTP_ACCEPT_LANGUAGE='en')
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
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key,
                                HTTP_ACCEPT='application/json; version=1.0',
                                HTTP_ACCEPT_LANGUAGE='en')
        response = self.client.delete(url)
        # test the response headers
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEquals(response['Content-Length'], '0')
        self.assertEquals(response['Content-Language'], 'en')
    
    
    @patch('tasks.export_tasks.ExportTaskRunner')
    def test_create_job(self, mock):
        task_runner = mock.return_value
        logger.debug('Mocked ExportTaskRunner: %s' % task_runner)
        url = reverse('api:jobs-list')
        formats = [str(format.uid) for format in ExportFormat.objects.all()]
        logger.debug(formats)
        request_data = {
            'name': 'TestJob',
            'description': 'Test description',
            'xmin': -7.96,
            'ymin': 22.6,
            'xmax': -8.14,
            'ymax': 27.12,
            'formats': formats
        }
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key,
                                HTTP_ACCEPT='application/json; version=1.0',
                                HTTP_ACCEPT_LANGUAGE='en',
                                HTTP_HOST='testserver')
        response = self.client.post(url, request_data)
        logger.debug(response)
        job_uid = response.data['uid']
        # test the ExportTaskRunner.run_task(job_id) method gets called.
        task_runner.run_task.assert_called_with(job_uid=job_uid)
        
        # test the response headers
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(response['Content-Type'], 'application/json; version=1.0')
        self.assertEquals(response['Content-Language'], 'en')
        logger.debug(response.data['formats'][0]['uid'])
        
        # test significant content
        self.assertEqual(response.data['formats'][0]['uid'], request_data['formats'][0])
        self.assertEqual(response.data['formats'][1]['uid'], request_data['formats'][1])
        self.assertEqual(response.data['name'], request_data['name'])
        self.assertEqual(response.data['description'], request_data['description'])
        #self.assertEqual(response.data['status'], 'PENDING')
    
    def test_validation(self, ):
        pass
    
        