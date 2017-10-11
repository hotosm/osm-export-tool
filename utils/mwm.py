# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging
import os
import shutil
import subprocess
import tempfile
from string import Template

from .artifact import Artifact

LOG = logging.getLogger(__name__)

def geos_to_poly(aoi,fname):
    with open(fname,'w') as f:
        f.write("export_bounds\n")
        if aoi.geom_type == 'MultiPolygon':
            for i, geom in enumerate(aoi.coords):
                f.write("{0}\n".format(i))
                for coord in geom[0]:
                    f.write("%f %f\n" % (coord[0],coord[1]))
                f.write("END\n")
        else:
            f.write("1\n")
            for coord in aoi.coords[0]:
                f.write("%f %f\n" % (coord[0],coord[1]))
            f.write("END\n")
        f.write("END")

class MWM(object):
    name = 'mwm'
    description = 'maps.me MWM'
    cmd = Template('generate_mwm.sh $input_pbf')

    def __init__(self, input_pbf, aoi_geom):
        """
        Initialize the MWM generation utility.

        Args:
            input_pbf: the source PBF
            aoi_geom: exported area
        """
        self.input_pbf = input_pbf
        self.aoi_geom = aoi_geom
        self.output = os.path.splitext(self.input_pbf)[0] + '.mwm'

    def run(self):
        if self.is_complete:
            LOG.debug("Skipping MWM, file exists")
            return

        borders_dir = tempfile.mkdtemp()
        polygon_file = os.path.join(borders_dir, os.path.splitext(os.path.split(self.input_pbf)[1])[0] + ".poly")
        geos_to_poly(self.aoi_geom, polygon_file)

        convert_cmd = self.cmd.safe_substitute({
            'input_pbf': self.input_pbf,
        })

        LOG.debug('Running: %s' % convert_cmd)

        tmpdir = tempfile.mkdtemp()
        env = os.environ.copy()
        env.update(
            HOME=tmpdir,
            MWM_WRITABLE_DIR=tmpdir,
            TARGET=os.path.dirname(self.output),
            BORDERS_PATH=borders_dir
        )

        try:
            subprocess.check_call(
                convert_cmd,
                env=env,
                shell=True,
                executable='/bin/bash')

            LOG.debug('generate_mwm.sh complete')
        finally:
            shutil.rmtree(borders_dir)
            shutil.rmtree(tmpdir)

    @property
    def results(self):
        return [Artifact([self.output], self.name)]

    @property
    def is_complete(self):
        return os.path.isfile(self.output)
