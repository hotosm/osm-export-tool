"""
    Harness for running export jobs against the dev database.
    From the project directory run:
    ./manage.py runscript export_task_test_harness --settings=hot_exports.settings -v2
    Depends on django-extensions.
"""
import os

from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry, Polygon

from oet2.jobs.models import ExportFormat, Job, Region, Tag
from oet2.jobs.presets import PresetParser
from oet2.tasks.task_runners import ExportTaskRunner


def run(*script_args):
    path = os.path.dirname(os.path.realpath(__file__))
    # pull out the demo user
    user = User.objects.get(username='bjohare')
    # create the test job
    bbox = Polygon.from_bbox((-10.85, 6.25, -10.62, 6.40))  # monrovia
    # bbox = Polygon.from_bbox((13.84,-33.87,34.05,-25.57))  #(w,s,e,n) horn of africa
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
            ExportFormat.objects.get(slug='thematic')
    ]
    job.formats = formats
    job.save()
    # add the tags (defaults to hdm presets)
    parser = PresetParser(preset='./tasks/tests/files/hdm_presets.xml')
    tags_dict = parser.parse()
    for entry in tags_dict:
        tag = Tag.objects.create(
            key=entry['key'],
            value=entry['value'],
            geom_types=entry['geom_types'],
            data_model='HDM',
            job=job
        )
    # run the export.. tasks processed on celery queue
    # results available at /api/runs url
    runner = ExportTaskRunner()
    runner.run_task(job_uid=str(job.uid))
