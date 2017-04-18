# noqa
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import shutil

from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template, render_to_string
from django.utils import timezone

from jobs.presets import TagParser

# Get an instance of a logger
logger = get_task_logger(__name__)



class ExportTask():
    pass

def osm_create_styles_task(self,
                          result={},
                          run_uid=None,
                          stage_dir=None,
                          job_name=None,
                          provider_slug=None,
                          bbox=None): # noqa
    """
    Task to create styles for osm.
    """
    self.update_task_state(run_uid, self.name)
    # input_gpkg = parse_result(result, 'geopackage')

    # TODO see if input_gpkg matches
    gpkg_file = '{0}-{1}-{2}.gpkg'.format(job_name,
                                          provider_slug,
                                          timezone.now().strftime('%Y%m%d'))
    style_file = os.path.join(
        stage_dir,
        '{0}-osm-{1}.qgs'.format(
            job_name,
            timezone.now().strftime("%Y%m%d")
        )
    )

    with open(style_file, 'w') as open_file:
        open_file.write(render_to_string('styles/Style.qgs', context={
            'gpkg_filename': os.path.basename(gpkg_file),
            'layer_id_prefix': '{0}-osm-{1}'.format(
                job_name,
                timezone.now().strftime("%Y%m%d")
            ),
            'layer_id_date_time': '{0}'.format(
                timezone.now().strftime("%Y%m%d%H%M%S%f")[
                    :-3]),
            'bbox': bbox}))

    self.on_success(style_file, run_uid, self.name)


class ObfExportTask(ExportTask):
    """Class defining OBF export function."""

    name = 'obf'
    description = 'OSMAnd OBF'

    def run(self, run_uid=None, stage_dir=None, job_name=None): # noqa
        self.update_task_state(run_uid, self.name)
        pbffile = '{0}.pbf'.format(os.path.join(stage_dir, job_name))
        map_creator_dir = settings.OSMAND_MAP_CREATOR_DIR
        work_dir = os.path.join(stage_dir, 'osmand')
        o2o = osmand.OSMToOBF(
            pbffile=pbffile, work_dir=work_dir, map_creator_dir=map_creator_dir
        )
        out = o2o.convert()
        obffile = '{0}.obf'.format(os.path.join(stage_dir, job_name))
        shutil.move(out, obffile)
        shutil.rmtree(work_dir)
        self.on_success(obffile, run_uid, self.name)
