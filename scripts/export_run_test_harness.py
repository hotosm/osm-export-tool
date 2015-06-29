"""
    Harness for running export jobs against the dev database.
    From the project directory run:
    ./manage.py runscript export_task_test_harness --settings=hot_exports.settings -v2
    Depends on django-extensions.
"""
import os
import logging
from jobs.models import Job, Tag, ExportFormat, Region
from tasks.task_runners import ExportTaskRunner
from django.contrib.auth.models import User
from jobs.presets import PresetParser
from django.contrib.gis.geos import GEOSGeometry, Polygon


def run(*script_args):
    path = os.path.dirname(os.path.realpath(__file__))
    # pull out the demo user
    user = User.objects.get(username='demo')
    # create the test job
    bbox = Polygon.from_bbox((-10.85,6.25,-10.62,6.40)) #monrovia
    #bbox = Polygon.from_bbox((13.84,-33.87,34.05,-25.57))  #(w,s,e,n) horn of africa
    the_geom = GEOSGeometry(bbox, srid=4326)
    job = Job.objects.create(name='TestJob',
                             description='Test description', user=user,
                             the_geom=the_geom)
    region = Region.objects.get(name='Africa')
    job.region = region
    job.save()
    # add the format(s)
    formats = [
            ExportFormat.objects.get(slug='obf'),
            ExportFormat.objects.get(slug='shp')
    ]
    job.formats = formats
    job.save()
    # add the tags (defaults to hdm presets)
    preset_parser = PresetParser(preset='./tasks/tests/files/hdm_presets.xml')
    tags = preset_parser.parse(merge_with_defaults=True)
    for key in tags:
        tag = Tag.objects.create(
            name = key,
            geom_types = tags[key]
        )
        job.tags.add(tag)
    # run the export.. tasks processed on celery queue
    # results available at /api/runs url
    runner = ExportTaskRunner()
    runner.run_task(job_uid=str(job.uid))

