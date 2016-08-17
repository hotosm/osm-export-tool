# -*- coding: utf-8 -*-
import logging

from django.contrib.auth.models import Group, User
from django.contrib.gis.geos import GEOSGeometry, Polygon
from django.test import TestCase
from django.utils import timezone

from oet2.jobs.models import Job
from oet2.tasks.scheduled_tasks import PurgeUnpublishedExportsTask

logger = logging.getLogger(__name__)


class TestPurgeUnpublishedExportsTask(TestCase):

    def setUp(self,):
        Group.objects.create(name='TestDefaultExportExtentGroup')
        self.user = User.objects.create(username='demo', email='demo@demo.com', password='demo')
        # bbox = Polygon.from_bbox((-7.96, 22.6, -8.14, 27.12))
        bbox = Polygon.from_bbox((-10.85, 6.25, -10.62, 6.40))
        the_geom = GEOSGeometry(bbox, srid=4326)
        created_at = timezone.now() - timezone.timedelta(hours=50)  # 50 hours ago
        Job.objects.create(name='TestJob', created_at=created_at, published=False,
                        description='Test description', user=self.user,
                        the_geom=the_geom)
        Job.objects.create(name='TestJob', created_at=created_at, published=True,
                        description='Test description', user=self.user,
                        the_geom=the_geom)

    def test_purge_export_jobs(self,):
        jobs = Job.objects.all()
        self.assertEquals(2, jobs.count())
        task = PurgeUnpublishedExportsTask()
        self.assertEquals('Purge Unpublished Exports', task.name)
        task.run()
        jobs = Job.objects.all()
        self.assertEquals(1, jobs.count())
        self.assertTrue(jobs[0].published)
