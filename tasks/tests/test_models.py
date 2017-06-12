# -*- coding: utf-8 -*-
import uuid

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.contrib.gis.geos import GEOSGeometry, Polygon
from django.test import TestCase
from django.utils import timezone
import datetime

from jobs.models import Job
from feature_selection.feature_selection import FeatureSelection

from ..models import ExportRun, ExportTask

class TestExportRunAndTask(TestCase):
    """
    Test cases for ExportRun model
    """

    def setUp(self,):
        self.user1 = User.objects.create(
            username='user1', 
            email='user1@demo.com', 
            password='demo'
        )
        the_geom = Polygon.from_bbox((-10.80029,6.3254236,-10.79809,6.32752))
        self.job = Job.objects.create(
            name='TestJob',
            user=self.user1,
            the_geom=the_geom,
            export_formats=['shp'],
            feature_selection=FeatureSelection.example('simple')
        )

    def test_export_run_duration(self, ):
        now = timezone.now()
        run = ExportRun.objects.create(
            job=self.job,
            user=self.user1,
            started_at=now,
            finished_at=now + datetime.timedelta(0,50)
        )
        self.assertIsNotNone(run.uid)
        self.assertEqual(run.duration,50)

    def test_export_task_duration(self):
        now = timezone.now()
        run = ExportRun.objects.create(
            job=self.job,
            user=self.user1
        )
        task1 = ExportTask.objects.create(
            run=run,
            started_at=now,
            finished_at=now + datetime.timedelta(0,50)
        )
        self.assertEqual(task1.duration,50)

    def test_get_runs_for_job_and_tasks_for_run(self, ):
        run1 = ExportRun.objects.create(
            job=self.job,
            user=self.user1
        )
        run2 = ExportRun.objects.create(
            job=self.job,
            user=self.user1
        )
        ExportTask.objects.create(
            run=run1
        )
        ExportTask.objects.create(
            run=run1
        )
        self.assertEqual(len(run1.tasks.all()),2)
        self.assertEqual(len(self.job.runs.all()),2)

    def test_download_url(self):
        run = ExportRun.objects.create(
            job=self.job,
            user=self.user1
        )
        task = ExportTask.objects.create(
            run=run,
            filenames = ['a_filename']
        )
        root = settings.EXPORT_MEDIA_ROOT
        self.assertEqual(task.download_url,root+str(run.uid)+'/'+'a_filename')



